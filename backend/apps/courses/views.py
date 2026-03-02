"""
Views для LMS: курсы, уроки, квизы.
"""
import logging
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import (
    Course, Lesson, Quiz, QuizQuestion, QuizAnswer,
    QuizAttempt, UserCourseProgress, UserLessonProgress,
)
from apps.tasks.models import ActivityLog
from .serializers import (
    CourseListSerializer, CourseDetailSerializer,
    LessonDetailSerializer, QuizAttemptResultSerializer,
    QuizAnswerWithCorrectSerializer, QuizQuestionSerializer,
)

logger = logging.getLogger(__name__)


# ─── Courses ──────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def course_list_view(request):
    """Список активных курсов с прогрессом пользователя."""
    courses = Course.objects.filter(is_active=True).prefetch_related(
        'modules', 'modules__lessons', 'prerequisites',
    )
    serializer = CourseListSerializer(courses, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def course_detail_view(request, slug):
    """Детали курса — модули, уроки, прогресс."""
    try:
        course = Course.objects.prefetch_related(
            'modules', 'modules__lessons', 'modules__lessons__user_progress',
            'prerequisites',
        ).get(slug=slug, is_active=True)
    except Course.DoesNotExist:
        return Response({'error': 'Курс не найден.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CourseDetailSerializer(course, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def course_enroll_view(request, slug):
    """Записаться на курс."""
    try:
        course = Course.objects.get(slug=slug, is_active=True)
    except Course.DoesNotExist:
        return Response({'error': 'Курс не найден.'}, status=status.HTTP_404_NOT_FOUND)

    progress, created = UserCourseProgress.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={
            'status': UserCourseProgress.STATUS_IN_PROGRESS,
            'started_at': timezone.now(),
        }
    )

    if not created and progress.status == UserCourseProgress.STATUS_NOT_STARTED:
        progress.status = UserCourseProgress.STATUS_IN_PROGRESS
        progress.started_at = timezone.now()
        progress.save(update_fields=['status', 'started_at'])

    return Response({
        'enrolled': True,
        'status': progress.status,
        'started_at': progress.started_at,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_progress_view(request, slug):
    """Прогресс пользователя по курсу."""
    try:
        course = Course.objects.get(slug=slug, is_active=True)
    except Course.DoesNotExist:
        return Response({'error': 'Курс не найден.'}, status=status.HTTP_404_NOT_FOUND)

    progress = UserCourseProgress.objects.filter(user=request.user, course=course).first()
    total = Lesson.objects.filter(module__course=course).count()
    completed = UserLessonProgress.objects.filter(
        user=request.user, lesson__module__course=course, completed=True,
    ).count()

    return Response({
        'status': progress.status if progress else 'not_started',
        'total_lessons': total,
        'completed_lessons': completed,
        'pct': round(completed / total * 100, 1) if total else 0,
        'started_at': progress.started_at if progress else None,
        'completed_at': progress.completed_at if progress else None,
    })


# ─── Skill Tree ───────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def skill_tree_view(request):
    """Дерево курсов для D3.js визуализации."""
    courses = Course.objects.filter(is_active=True).prefetch_related('prerequisites')

    completed_ids = set()
    in_progress_ids = set()
    if request.user.is_authenticated:
        for p in UserCourseProgress.objects.filter(user=request.user):
            if p.status == UserCourseProgress.STATUS_COMPLETED:
                completed_ids.add(p.course_id)
            elif p.status == UserCourseProgress.STATUS_IN_PROGRESS:
                in_progress_ids.add(p.course_id)

    nodes = []
    edges = []

    for course in courses:
        prereq_ids = [p.id for p in course.prerequisites.all()]
        prereqs_met = all(pid in completed_ids for pid in prereq_ids)

        if course.id in completed_ids:
            node_status = 'completed'
        elif course.id in in_progress_ids:
            node_status = 'in_progress'
        elif prereqs_met:
            node_status = 'available'
        else:
            node_status = 'locked'

        nodes.append({
            'id': course.slug,
            'course_id': course.id,
            'title_ru': course.title_ru,
            'icon': course.icon,
            'difficulty': course.difficulty,
            'estimated_hours': course.estimated_hours,
            'xp_reward': course.xp_reward,
            'category': course.category,
            'status': node_status,
        })

        for prereq in course.prerequisites.all():
            edges.append({'source': prereq.slug, 'target': course.slug})

    return Response({'nodes': nodes, 'edges': edges})


# ─── Lessons ──────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def lesson_detail_view(request, lesson_id):
    """Контент урока — теория, квиз, лаба."""
    try:
        lesson = Lesson.objects.select_related(
            'module__course', 'task',
        ).prefetch_related(
            'quiz__questions__answers', 'user_progress',
        ).get(id=lesson_id)
    except Lesson.DoesNotExist:
        return Response({'error': 'Урок не найден.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = LessonDetailSerializer(lesson, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def lesson_complete_view(request, lesson_id):
    """Отметить теорию как прочитанную → начислить XP (один раз)."""
    try:
        lesson = Lesson.objects.get(id=lesson_id)
    except Lesson.DoesNotExist:
        return Response({'error': 'Урок не найден.'}, status=status.HTTP_404_NOT_FOUND)

    if lesson.lesson_type != Lesson.TYPE_THEORY:
        return Response({'error': 'Только теоретические уроки можно отметить прочитанными.'}, status=400)

    prog, created = UserLessonProgress.objects.get_or_create(
        user=request.user, lesson=lesson,
    )
    first_time = not prog.completed

    if not prog.completed:
        prog.viewed = True
        prog.completed = True
        prog.completed_at = timezone.now()
        prog.save(update_fields=['viewed', 'completed', 'completed_at'])
        prog._check_course_progress()
    elif not prog.viewed:
        prog.viewed = True
        prog.save(update_fields=['viewed'])

    xp_earned = 0
    if first_time:
        xp_earned = lesson.xp_reward
        request.user.add_xp(xp_earned)
        ActivityLog.objects.create(
            user=request.user,
            action=ActivityLog.ACTION_LESSON_COMPLETED,
            metadata={'lesson_id': lesson.id, 'xp_earned': xp_earned},
        )

    return Response({
        'completed': True,
        'xp_earned': xp_earned,
    })


# ─── Quiz ─────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quiz_submit_view(request, quiz_id):
    """
    Сдать квиз.
    Body: {"answers": {"<question_id>": [<answer_id>, ...]}}
    """
    try:
        quiz = Quiz.objects.prefetch_related('questions__answers').get(id=quiz_id)
    except Quiz.DoesNotExist:
        return Response({'error': 'Тест не найден.'}, status=status.HTTP_404_NOT_FOUND)

    answers_input = request.data.get('answers', {})
    if not isinstance(answers_input, dict):
        return Response({'error': 'answers должен быть объектом {question_id: [answer_id]}'}, status=400)

    questions = list(quiz.questions.prefetch_related('answers').all())
    total = len(questions)
    if total == 0:
        return Response({'error': 'Тест не содержит вопросов.'}, status=400)

    correct_count = 0
    results = []

    for question in questions:
        qid = str(question.id)
        selected_ids = set(int(x) for x in answers_input.get(qid, []))
        correct_ids = set(question.answers.filter(is_correct=True).values_list('id', flat=True))
        is_correct = selected_ids == correct_ids
        if is_correct:
            correct_count += 1

        results.append({
            'question_id': question.id,
            'question_text': question.text_ru,
            'is_correct': is_correct,
            'explanation_ru': question.explanation_ru,
            'answers': QuizAnswerWithCorrectSerializer(question.answers.all(), many=True).data,
            'selected_ids': list(selected_ids),
        })

    score = round(correct_count / total * 100)
    passed = score >= quiz.pass_threshold

    xp_earned = 0
    if passed:
        xp_earned = quiz.lesson.xp_reward
        request.user.add_xp(xp_earned)

        # Обновляем прогресс урока
        prog, _ = UserLessonProgress.objects.get_or_create(
            user=request.user, lesson=quiz.lesson,
        )
        if not prog.quiz_passed:
            prog.quiz_passed = True
            prog.mark_completed()
            ActivityLog.objects.create(
                user=request.user,
                action=ActivityLog.ACTION_QUIZ_PASSED,
                metadata={'quiz_id': quiz.id, 'score': score, 'xp_earned': xp_earned},
            )

    attempt = QuizAttempt.objects.create(
        user=request.user,
        quiz=quiz,
        score=score,
        passed=passed,
        answers_snapshot=answers_input,
        xp_earned=xp_earned,
    )

    return Response({
        'attempt_id': attempt.id,
        'score': score,
        'passed': passed,
        'correct_count': correct_count,
        'total': total,
        'xp_earned': xp_earned,
        'pass_threshold': quiz.pass_threshold,
        'results': results,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quiz_attempts_view(request, quiz_id):
    """История попыток прохождения квиза."""
    attempts = QuizAttempt.objects.filter(
        user=request.user, quiz_id=quiz_id,
    ).order_by('-created_at')[:10]
    serializer = QuizAttemptResultSerializer(attempts, many=True)
    return Response(serializer.data)
