"""
API для Daily Challenge (задача дня).
"""
import logging
from datetime import date

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Task, DailyChallenge, DailyChallengeCompletion, UserTask

logger = logging.getLogger(__name__)


def _serialize_challenge(challenge, user):
    """Сериализует DailyChallenge с данными о выполнении пользователя."""
    task = challenge.task

    # Проверяем выполнил ли пользователь
    my_completion = DailyChallengeCompletion.objects.filter(
        user=user, challenge=challenge
    ).first()

    # Таблица лидеров — топ-10 по времени
    leaderboard = []
    top = DailyChallengeCompletion.objects.filter(
        challenge=challenge
    ).order_by('time_spent').select_related('user')[:10]

    for i, entry in enumerate(top, 1):
        leaderboard.append({
            'rank': i,
            'username': entry.user.username,
            'time_spent': entry.time_spent,
            'xp_earned': entry.xp_earned,
        })

    return {
        'id': challenge.id,
        'date': challenge.date.isoformat(),
        'participants_count': challenge.participants_count,
        'completions_count': challenge.completions_count,
        'task': {
            'id': task.id,
            'title_ru': task.title_ru,
            'description_ru': task.description_ru,
            'category': task.category,
            'category_display': task.category_display,
            'difficulty': task.difficulty,
            'difficulty_display': task.difficulty_display,
            'xp_reward': task.xp_reward,
        },
        'my_completion': {
            'completed': True,
            'time_spent': my_completion.time_spent,
            'xp_earned': my_completion.xp_earned,
            'completed_at': my_completion.completed_at.isoformat(),
        } if my_completion else None,
        'leaderboard': leaderboard,
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def daily_challenge_view(request):
    """
    Возвращает задачу дня и таблицу лидеров.
    Если задача на сегодня не назначена — берём последнюю доступную.
    """
    today = date.today()
    challenge = DailyChallenge.objects.filter(date=today).select_related('task').first()

    if not challenge:
        # Ещё не создана на сегодня — берём последнюю
        challenge = DailyChallenge.objects.select_related('task').first()

    if not challenge:
        # Нет ни одной задачи дня — создаём из случайной задачи
        task = Task.objects.filter(is_active=True).order_by('?').first()
        if not task:
            return Response(
                {'error': 'Нет доступных задач.'},
                status=status.HTTP_404_NOT_FOUND
            )
        challenge = DailyChallenge.objects.create(task=task, date=today)

    return Response(_serialize_challenge(challenge, request.user))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def daily_challenge_start_view(request):
    """
    Начать Daily Challenge.
    Увеличивает счётчик participants_count.
    Body: {} (без параметров)
    """
    today = date.today()
    challenge = DailyChallenge.objects.filter(date=today).first()

    if not challenge:
        return Response(
            {'error': 'Задача дня не найдена.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Не начинали ещё?
    already_completed = DailyChallengeCompletion.objects.filter(
        user=request.user, challenge=challenge
    ).exists()
    if already_completed:
        return Response({'message': 'Уже выполнено.'})

    # Увеличиваем счётчик участников (один раз при первом старте)
    DailyChallenge.objects.filter(pk=challenge.pk).update(
        participants_count=challenge.participants_count + 1
    )

    return Response({
        'task_id': challenge.task_id,
        'message': 'Задача дня начата! Удачи!',
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def daily_challenge_complete_view(request):
    """
    Завершить Daily Challenge.
    Body: {time_spent: int}  — секунды с момента начала
    Начисляет XP с бонусом +20%.
    """
    today = date.today()
    challenge = DailyChallenge.objects.filter(date=today).select_related('task').first()

    if not challenge:
        return Response(
            {'error': 'Задача дня не найдена.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Уже выполнено?
    if DailyChallengeCompletion.objects.filter(user=request.user, challenge=challenge).exists():
        return Response({'message': 'Ты уже выполнил задачу дня!'})

    # Проверяем что задача действительно выполнена через UserTask
    user_task = UserTask.objects.filter(
        user=request.user,
        task=challenge.task,
        status=UserTask.STATUS_COMPLETED,
    ).first()

    if not user_task:
        return Response(
            {'error': 'Сначала выполни задачу в терминале.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    time_spent = request.data.get('time_spent', user_task.time_spent or 0)

    # XP с бонусом +20% за daily challenge
    base_xp = challenge.task.xp_reward
    daily_xp = round(base_xp * 1.2)

    # Начисляем XP пользователю
    request.user.add_xp(daily_xp)

    # Записываем выполнение
    DailyChallengeCompletion.objects.create(
        user=request.user,
        challenge=challenge,
        time_spent=time_spent,
        xp_earned=daily_xp,
    )

    # Обновляем счётчик
    DailyChallenge.objects.filter(pk=challenge.pk).update(
        completions_count=challenge.completions_count + 1
    )

    logger.info(
        f'Daily Challenge выполнен: {request.user.username} '
        f'({challenge.date}, {time_spent}s, +{daily_xp} XP)'
    )

    return Response({
        'xp_earned': daily_xp,
        'time_spent': time_spent,
        'message': f'+{daily_xp} XP за задачу дня!',
    })
