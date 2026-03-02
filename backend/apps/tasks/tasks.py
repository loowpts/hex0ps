"""
Celery задачи для приложения tasks.
"""
import logging
from datetime import date, timedelta

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name='apps.tasks.pick_daily_challenge')
def pick_daily_challenge():
    """
    Выбирает задачу дня на завтра.
    Запускается каждый день в 00:00 UTC через Celery Beat.

    Алгоритм:
    - Берём задачи с difficulty=intermediate, is_active=True
    - Исключаем задачи, которые уже были daily за последние 30 дней
    - Выбираем ту, которая дольше всего не использовалась как daily
    """
    from .models import Task, DailyChallenge

    tomorrow = date.today() + timedelta(days=1)

    # Проверяем — уже назначена задача на завтра?
    if DailyChallenge.objects.filter(date=tomorrow).exists():
        logger.info(f'Daily challenge на {tomorrow} уже назначен.')
        return

    # Задачи использованные за последние 30 дней
    recent_cutoff = date.today() - timedelta(days=30)
    recently_used = DailyChallenge.objects.filter(
        date__gte=recent_cutoff
    ).values_list('task_id', flat=True)

    # Выбираем кандидата: intermediate задачи, не использованные недавно
    candidates = Task.objects.filter(
        is_active=True,
        difficulty='intermediate',
    ).exclude(
        id__in=recently_used
    ).order_by('?')  # случайный порядок

    if not candidates.exists():
        # Фолбэк — любая active задача
        candidates = Task.objects.filter(is_active=True).exclude(
            id__in=recently_used
        ).order_by('?')

    if not candidates.exists():
        # Самый крайний случай — берём любую задачу
        candidates = Task.objects.filter(is_active=True).order_by('?')

    if not candidates.exists():
        logger.error('Нет активных задач для Daily Challenge!')
        return

    task = candidates.first()
    DailyChallenge.objects.create(task=task, date=tomorrow)
    logger.info(f'Daily Challenge на {tomorrow} назначен: {task.title_ru}')
