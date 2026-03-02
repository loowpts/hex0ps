import logging
import functools
import redis as redis_client
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)

AI_RATE_LIMIT = 10
AI_RATE_WINDOW = 60


def check_rate_limit(user_id: int) -> bool:
    try:
        r = redis_client.from_url(settings.REDIS_URL)
        key = f'ai:rate:{user_id}'
        current = r.incr(key)
        if current == 1:
            r.expire(key, AI_RATE_WINDOW)
        return current <= AI_RATE_LIMIT
    except Exception as e:
        logger.warning(f'Redis rate limit error: {e}')
        return False


def ai_rate_limited(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not check_rate_limit(request.user.id):
            return Response(
                {'error': 'Слишком много запросов к AI. Подожди немного.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        return view_func(request, *args, **kwargs)
    return wrapper


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ai_rate_limited
def ai_hint_view(request):
    task_id = request.data.get('task_id')
    terminal_output = request.data.get('terminal_output', '')

    if not task_id:
        return Response({'error': 'task_id обязателен.'}, status=status.HTTP_400_BAD_REQUEST)

    from apps.tasks.models import Task
    try:
        task = Task.objects.get(id=task_id, is_active=True)
    except Task.DoesNotExist:
        return Response({'error': 'Задача не найдена.'}, status=status.HTTP_404_NOT_FOUND)

    hint = OllamaClient().generate_hint(task, terminal_output)
    return Response({'hint': hint, 'type': 'question'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ai_rate_limited
def ai_explain_view(request):
    question = request.data.get('question', '').strip()
    context = request.data.get('context', '')

    if not question:
        return Response({'error': 'Вопрос не может быть пустым.'}, status=status.HTTP_400_BAD_REQUEST)

    prompt = f'Контекст: {context}\n\nВопрос: {question}' if context else question
    explanation = OllamaClient().generate(prompt)

    if not explanation:
        explanation = 'AI временно недоступен. Обратись к документации или Stack Overflow.'

    return Response({'explanation': explanation})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ai_rate_limited
def ai_ask_view(request):
    question = request.data.get('question', '').strip()
    task_id = request.data.get('task_id')
    context = request.data.get('context', '')

    if not question:
        return Response({'error': 'Вопрос не может быть пустым.'}, status=status.HTTP_400_BAD_REQUEST)

    prompt = question
    if task_id:
        from apps.tasks.models import Task
        try:
            task = Task.objects.get(id=task_id)
            prompt = f'Контекст задачи: {task.title_ru}\n{task.description_ru}\n\nВопрос: {question}'
        except Task.DoesNotExist:
            pass
    elif context:
        prompt = f'Контекст: {context}\n\nВопрос: {question}'

    answer = OllamaClient().generate(prompt)

    if not answer:
        answer = 'AI временно недоступен. Обратись к документации или man-страницам.'

    return Response({'answer': answer})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ai_rate_limited
def ai_explain_lesson_view(request):
    lesson_title = request.data.get('lesson_title', '').strip()
    selected_text = request.data.get('selected_text', '').strip()

    if not selected_text:
        return Response({'error': 'Выделенный текст не может быть пустым.'}, status=status.HTTP_400_BAD_REQUEST)

    explanation = OllamaClient().explain_lesson_content(lesson_title, selected_text)
    return Response({'explanation': explanation})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ai_rate_limited
def ai_generate_task_view(request):
    category = request.data.get('category', 'linux')
    difficulty = request.data.get('difficulty', 'beginner')
    task_type = request.data.get('task_type', 'regular')

    valid_categories = ['linux', 'nginx', 'systemd', 'docker', 'networks', 'git', 'cicd']
    valid_difficulties = ['beginner', 'intermediate', 'advanced']
    valid_types = ['regular', 'break_and_fix']

    if category not in valid_categories:
        return Response({'error': f'Неверная категория. Допустимые: {valid_categories}'}, status=400)
    if difficulty not in valid_difficulties:
        return Response({'error': f'Неверная сложность. Допустимые: {valid_difficulties}'}, status=400)
    if task_type not in valid_types:
        return Response({'error': f'Неверный тип. Допустимые: {valid_types}'}, status=400)

    task_data = OllamaClient().generate_task(category, difficulty, task_type)

    if not task_data:
        return Response(
            {'error': 'Не удалось сгенерировать задачу. Попробуй позже.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    from apps.tasks.models import Task
    try:
        task = Task.objects.create(
            title_ru=task_data.get('title_ru', 'Задача без названия'),
            description_ru=task_data.get('description_ru', ''),
            hint_1_ru=task_data.get('hint_1_ru', ''),
            hint_2_ru=task_data.get('hint_2_ru', ''),
            hint_3_ru=task_data.get('hint_3_ru', ''),
            category=category,
            difficulty=difficulty,
            task_type=task_type,
            xp_reward=task_data.get('xp_reward', 150),
            time_limit=task_data.get('time_limit', 30),
            docker_image=f'devops-platform/{category}:latest',
            checker_type=task_data.get('checker_type', 'command_output'),
            checker_config=task_data.get('checker_config', {}),
            solution_steps=task_data.get('solution_steps', []),
            is_active=False,
        )
        return Response(
            {'task_id': task.id, 'message': 'Задача создана и ожидает проверки модератором.'},
            status=status.HTTP_201_CREATED,
        )
    except Exception as e:
        logger.error(f'Ошибка сохранения сгенерированной задачи: {e}')
        return Response({'error': 'Ошибка сохранения задачи.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
