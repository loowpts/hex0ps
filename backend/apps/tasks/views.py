import logging
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Task, UserTask, ActivityLog
from .serializers import TaskListSerializer, TaskDetailSerializer
from .throttles import TaskStartThrottle, TaskCheckThrottle
from .constants import XP_BONUS_NO_HINTS, XP_BONUS_STREAK, STREAK_BONUS_THRESHOLD, XP_HINT_MULTIPLIERS

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def task_list_view(request):
    queryset = Task.objects.filter(is_active=True).prefetch_related('prerequisites', 'user_tasks')

    category = request.query_params.get('category')
    if category:
        queryset = queryset.filter(category=category)

    difficulty = request.query_params.get('difficulty')
    if difficulty:
        queryset = queryset.filter(difficulty=difficulty)

    task_type = request.query_params.get('task_type')
    if task_type:
        queryset = queryset.filter(task_type=task_type)

    if request.user.is_authenticated:
        user_status = request.query_params.get('status')
        if user_status == 'completed':
            queryset = queryset.filter(user_tasks__user=request.user, user_tasks__status='completed')
        elif user_status == 'in_progress':
            queryset = queryset.filter(user_tasks__user=request.user, user_tasks__status='in_progress')
        elif user_status == 'not_started':
            completed_ids = UserTask.objects.filter(
                user=request.user,
                status__in=['completed', 'in_progress']
            ).values_list('task_id', flat=True)
            queryset = queryset.exclude(id__in=completed_ids)

    # Prefetch user progress to avoid N+1 in serializer
    context = {'request': request}
    if request.user.is_authenticated:
        user_tasks_qs = UserTask.objects.filter(user=request.user).values('task_id', 'status')
        context['user_task_statuses'] = {ut['task_id']: ut['status'] for ut in user_tasks_qs}
        context['completed_ids'] = {
            tid for tid, st in context['user_task_statuses'].items() if st == 'completed'
        }

    serializer = TaskListSerializer(queryset, many=True, context=context)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def task_detail_view(request, task_id):
    try:
        task = Task.objects.prefetch_related('prerequisites', 'user_tasks').get(
            id=task_id,
            is_active=True
        )
    except Task.DoesNotExist:
        return Response({'error': 'Задача не найдена.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TaskDetailSerializer(task, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([TaskStartThrottle])
def task_start_view(request, task_id):
    try:
        task = Task.objects.prefetch_related('prerequisites').get(id=task_id, is_active=True)
    except Task.DoesNotExist:
        return Response({'error': 'Задача не найдена.'}, status=status.HTTP_404_NOT_FOUND)

    user = request.user

    prerequisites = task.prerequisites.all()
    if prerequisites:
        completed_ids = set(
            UserTask.objects.filter(user=user, status='completed').values_list('task_id', flat=True)
        )
        missing = [p for p in prerequisites if p.id not in completed_ids]
        if missing:
            missing_titles = ', '.join(p.title_ru for p in missing)
            return Response(
                {'error': f'Сначала выполни: {missing_titles}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    from apps.terminal.models import TerminalSession
    active_session = TerminalSession.objects.filter(user=user, status='active').first()
    if active_session:
        return Response(
            {'error': 'У тебя уже есть активный терминал. Заверши его перед началом новой задачи.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user_task, created = UserTask.objects.get_or_create(
        user=user,
        task=task,
        defaults={
            'status': UserTask.STATUS_IN_PROGRESS,
            'started_at': timezone.now(),
            'attempts': 1,
        }
    )

    if not created:
        user_task.attempts += 1
        if not user_task.started_at:
            user_task.started_at = timezone.now()
        if user_task.status != UserTask.STATUS_COMPLETED:
            user_task.status = UserTask.STATUS_IN_PROGRESS
        user_task.save(update_fields=['status', 'attempts', 'started_at'])

    expires_at = timezone.now() + timezone.timedelta(minutes=task.time_limit)
    session = TerminalSession.objects.create(
        user=user,
        task=task,
        status='pending',
        expires_at=expires_at,
    )

    ActivityLog.objects.create(
        user=user,
        action=ActivityLog.ACTION_TASK_STARTED,
        metadata={
            'task_id': task.id,
            'task_title': task.title_ru,
            'category': task.category,
        }
    )

    return Response({
        'session_id': str(session.id),
        'task_id': task.id,
        'expires_at': session.expires_at.isoformat(),
        'time_remaining_seconds': session.time_remaining_seconds(),
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([TaskCheckThrottle])
def task_check_view(request, task_id):
    try:
        task = Task.objects.get(id=task_id, is_active=True)
    except Task.DoesNotExist:
        return Response({'error': 'Задача не найдена.'}, status=status.HTTP_404_NOT_FOUND)

    user = request.user

    from apps.terminal.models import TerminalSession
    session = TerminalSession.objects.filter(
        user=user,
        task=task,
        status__in=['active', 'pending']
    ).order_by('-created_at').first()
    if not session:
        return Response(
            {'error': 'Активная сессия не найдена. Начни задачу заново.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if session.is_expired():
        return Response({'error': 'Время вышло! Начни задачу заново.'}, status=status.HTTP_400_BAD_REQUEST)

    # Checker runs outside transaction — does Docker exec (I/O, up to 15s)
    from apps.tasks.checker import run_checker
    success, message = run_checker(task, session.container_id)

    if not success:
        return Response({'success': False, 'message': message})

    # All DB writes in one atomic transaction with row-level lock
    with transaction.atomic():
        try:
            user_task = UserTask.objects.select_for_update().get(user=user, task=task)
        except UserTask.DoesNotExist:
            return Response(
                {'error': 'Прогресс по задаче не найден.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        first_completion = user_task.completed_at is None
        multiplier = user_task.calculate_xp_multiplier()

        # Бонус за решение без подсказок
        if user_task.hints_used == 0:
            multiplier *= XP_BONUS_NO_HINTS

        # Бонус за активный стрик
        if user.streak >= STREAK_BONUS_THRESHOLD:
            multiplier *= XP_BONUS_STREAK

        xp_earned = int(task.xp_reward * multiplier)
        time_spent = int((timezone.now() - user_task.started_at).total_seconds()) if user_task.started_at else 0

        user_task.status = UserTask.STATUS_COMPLETED
        user_task.xp_earned = xp_earned
        user_task.xp_multiplier = multiplier
        if first_completion:
            user_task.completed_at = timezone.now()
        user_task.time_spent = time_spent
        user_task.save()

        # XP awarded only on first completion
        if first_completion:
            user.add_xp(xp_earned)

        user.update_streak()

        session.status = 'completed'
        session.save(update_fields=['status'])

        if first_completion:
            ActivityLog.objects.create(
                user=user,
                action=ActivityLog.ACTION_TASK_COMPLETED,
                metadata={
                    'task_id': task.id,
                    'task_title': task.title_ru,
                    'category': task.category,
                    'xp_earned': xp_earned,
                    'time_spent': time_spent,
                    'hints_used': user_task.hints_used,
                }
            )

        from apps.users.achievements import check_and_award_achievements
        new_achievements = check_and_award_achievements(user)
        new_certificate = _check_category_certificate(user, task.category)

    # Remove container after transaction commit
    if session.container_id:
        from apps.terminal.tasks import remove_container_async
        remove_container_async.delay(session.container_id, session.id)

    # Invalidate analytics cache
    cache.delete(f'analytics_me:{user.id}')

    return Response({
        'success': True,
        'message': 'Задача выполнена! Отличная работа!',
        'xp_earned': xp_earned,
        'xp_multiplier': round(multiplier, 2),
        'new_achievements': new_achievements,
        'new_certificate': new_certificate,
        'level_up': None,
        'user_level': user.level,
        'user_xp': user.xp,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def task_hint_view(request, task_id):
    try:
        task = Task.objects.get(id=task_id, is_active=True)
    except Task.DoesNotExist:
        return Response({'error': 'Задача не найдена.'}, status=status.HTTP_404_NOT_FOUND)

    hint_level = request.data.get('level')
    try:
        hint_level = int(hint_level)
    except (TypeError, ValueError):
        hint_level = None
    if hint_level not in [1, 2, 3]:
        return Response(
            {'error': 'Уровень подсказки должен быть 1, 2 или 3.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = request.user

    try:
        user_task = UserTask.objects.get(user=user, task=task)
    except UserTask.DoesNotExist:
        return Response({'error': 'Сначала начни задачу.'}, status=status.HTTP_400_BAD_REQUEST)

    # Нельзя пропускать уровни подсказок
    if hint_level > user_task.hints_used + 1:
        return Response(
            {'error': f'Сначала открой подсказку уровня {user_task.hints_used + 1}.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if hint_level <= user_task.hints_used:
        hint_text = getattr(task, f'hint_{hint_level}_ru')
        return Response({
            'hint_text': hint_text,
            'xp_multiplier': user_task.xp_multiplier,
            'hints_remaining': 3 - user_task.hints_used,
        })

    user_task.hints_used = hint_level
    user_task.xp_multiplier = XP_HINT_MULTIPLIERS[hint_level]
    user_task.save(update_fields=['hints_used', 'xp_multiplier'])

    ActivityLog.objects.create(
        user=user,
        action=ActivityLog.ACTION_HINT_USED,
        metadata={'task_id': task.id, 'hint_level': hint_level}
    )

    hint_text = getattr(task, f'hint_{hint_level}_ru')
    return Response({
        'hint_text': hint_text,
        'xp_multiplier': user_task.xp_multiplier,
        'hints_remaining': 3 - hint_level,
        'message': _get_hint_message(hint_level),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_replay_view(request, task_id):
    try:
        task = Task.objects.get(id=task_id, is_active=True)
    except Task.DoesNotExist:
        return Response({'error': 'Задача не найдена.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        user_task = UserTask.objects.get(
            user=request.user,
            task=task,
            status=UserTask.STATUS_COMPLETED
        )
    except UserTask.DoesNotExist:
        return Response(
            {'error': 'Сначала выполни задачу, чтобы увидеть эталонное решение.'},
            status=status.HTTP_403_FORBIDDEN
        )

    return Response({
        'task_id': task.id,
        'title_ru': task.title_ru,
        'solution_steps': task.solution_steps,
        'completed_at': user_task.completed_at,
    })


def _get_hint_message(level: int) -> str:
    messages = {
        1: 'Подсказка 1 открыта. XP не изменился.',
        2: 'Подсказка 2 открыта. Награда уменьшена до 75% XP.',
        3: 'Подсказка 3 открыта. Награда уменьшена до 50% XP.',
    }
    return messages.get(level, '')


def _check_category_certificate(user, category: str) -> dict | None:
    try:
        from apps.certs.models import Certificate

        if Certificate.objects.filter(user=user, category=category).exists():
            return None

        total = Task.objects.filter(category=category, is_active=True).count()
        if total == 0:
            return None

        completed = UserTask.objects.filter(
            user=user,
            task__category=category,
            status='completed'
        ).count()

        if completed >= total:
            cert = Certificate.objects.create(user=user, category=category)
            from apps.certs.tasks import generate_certificate_pdf
            generate_certificate_pdf.delay(cert.id)
            return {
                'category': category,
                'cert_id': str(cert.cert_id),
                'message': f'Поздравляем! Ты получил сертификат по категории {category}!',
            }
    except Exception as e:
        logger.error(f'Certificate check error: {e}')

    return None
