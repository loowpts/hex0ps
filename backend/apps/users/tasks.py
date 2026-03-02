"""
Celery задачи для работы со стриками и уведомлениями пользователей.
"""
import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def check_streak_notifications():
    """
    Ежедневная задача в 20:00 — предупреждает пользователей о риске потери стрика.
    Находит активных пользователей, которые не заходили сегодня.
    """
    from apps.users.models import User

    today = timezone.now().date()

    # Пользователи со стриком > 0, которые не заходили сегодня
    at_risk_users = User.objects.filter(
        streak__gt=0,
        last_active__lt=today,
        is_active=True,
    )

    created_count = 0
    for user in at_risk_users:
        try:
            # Создаём уведомление о риске потери стрика
            from apps.analytics.models import Notification
            Notification.objects.get_or_create(
                user=user,
                type='streak_at_risk',
                defaults={
                    'message': f'Твой стрик {user.streak} дней под угрозой! '
                               f'Зайди и реши хотя бы одну задачу сегодня.'
                }
            )
            created_count += 1
        except Exception as e:
            logger.error(f'Ошибка создания уведомления для {user.email}: {e}')

    logger.info(f'Создано {created_count} уведомлений о риске стрика')
    return created_count
