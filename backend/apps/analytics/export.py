"""
Экспорт прогресса пользователя в PDF.
"""
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


def generate_progress_report(user) -> bytes | None:
    """
    Генерирует PDF-отчёт о прогрессе пользователя.

    Содержит:
    - Имя пользователя, уровень, XP
    - Навыки по категориям с визуальными барами
    - Список выполненных задач по категориям
    - Достижения
    - Сертификаты

    Возвращает bytes (PDF) или None при ошибке.
    """
    try:
        from weasyprint import HTML
        from django.template.loader import render_to_string
        from apps.tasks.models import UserTask, Task
        from apps.users.achievements import get_user_achievements_data
        from apps.certs.models import Certificate

        # --- Собираем данные ---
        categories = ['linux', 'nginx', 'systemd', 'docker', 'networks', 'git', 'cicd']

        completed_tasks = UserTask.objects.filter(
            user=user, status='completed'
        ).select_related('task').order_by('completed_at')

        skills = {}
        for cat in categories:
            total = Task.objects.filter(category=cat, is_active=True).count()
            completed_count = sum(1 for ut in completed_tasks if ut.task.category == cat)
            pct = round(completed_count / total * 100) if total > 0 else 0
            skills[cat] = {
                'completed': completed_count,
                'total': total,
                'pct': pct,
                'bar_width': pct,
            }

        # Задачи по категориям
        tasks_by_category = {}
        for cat in categories:
            cat_tasks = [ut for ut in completed_tasks if ut.task.category == cat]
            if cat_tasks:
                tasks_by_category[cat] = cat_tasks

        # Достижения
        achievements = get_user_achievements_data(user)

        # Сертификаты
        certificates = Certificate.objects.filter(user=user).order_by('issued_at')

        # --- Рендерим HTML ---
        context = {
            'user': user,
            'skills': skills,
            'tasks_by_category': tasks_by_category,
            'achievements': achievements,
            'certificates': certificates,
            'generated_at': timezone.now(),
            'total_completed': completed_tasks.count(),
            'level_pct': user.level_progress_pct,
        }

        html_string = render_to_string('analytics/progress_report.html', context)
        pdf_bytes = HTML(string=html_string).write_pdf()
        return pdf_bytes

    except ImportError:
        logger.error('WeasyPrint не установлен. Установи: pip install weasyprint')
        return None
    except Exception as e:
        logger.error(f'Ошибка генерации PDF-отчёта для {user.username}: {e}')
        return None
