"""
Celery задачи для управления Docker-контейнерами.
"""
import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def cleanup_expired_sessions():
    """
    Запускается каждую минуту через Celery Beat.
    Находит истёкшие TerminalSession и PlaygroundSession и удаляет контейнеры.
    """
    from apps.terminal.models import TerminalSession, PlaygroundSession
    from apps.terminal.docker_manager import DockerManager

    now = timezone.now()
    docker = DockerManager()
    cleaned = 0

    # --- TerminalSession (задачи) ---
    expired_terminal = TerminalSession.objects.filter(
        status='active',
        expires_at__lt=now,
    )
    for session in expired_terminal:
        try:
            if session.container_id:
                docker.remove_container(session.container_id)
            session.status = 'expired'
            session.save(update_fields=['status'])
            cleaned += 1
            logger.info(f'Очищена истёкшая terminal-сессия {session.id} пользователя {session.user_id}')
        except Exception as e:
            logger.error(f'Ошибка очистки terminal-сессии {session.id}: {e}')

    # --- PlaygroundSession (свободный терминал) ---
    expired_playground = PlaygroundSession.objects.filter(
        status='active',
        expires_at__lt=now,
    )
    for session in expired_playground:
        try:
            if session.container_id:
                docker.remove_container(session.container_id)
            session.status = 'expired'
            session.save(update_fields=['status'])
            cleaned += 1
            logger.info(f'Очищена истёкшая playground-сессия {session.id} пользователя {session.user_id}')
        except Exception as e:
            logger.error(f'Ошибка очистки playground-сессии {session.id}: {e}')

    if cleaned:
        logger.info(f'Итого очищено {cleaned} истёкших сессий')
    return cleaned


@shared_task
def remove_container_async(container_id: str, session_id: int):
    """
    Асинхронное удаление контейнера после завершения задачи.
    Вызывается из task_check_view.
    """
    from apps.terminal.docker_manager import DockerManager

    try:
        docker = DockerManager()
        docker.remove_container(container_id)
        logger.info(f'Асинхронно удалён контейнер {container_id[:12]} для сессии {session_id}')
    except Exception as e:
        logger.error(f'Ошибка асинхронного удаления контейнера: {e}')
