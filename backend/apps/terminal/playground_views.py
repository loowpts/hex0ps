"""
API для Playground — свободного терминала без задачи.
"""
import logging
from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import PlaygroundSession

logger = logging.getLogger(__name__)

PLAYGROUND_DURATION_MINUTES = 30


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def playground_environments_view(request):
    """Список доступных окружений для Playground."""
    return Response({
        'environments': [
            {
                'id': PlaygroundSession.ENV_UBUNTU,
                'label': 'Ubuntu 22.04',
                'description': 'Чистая Ubuntu с базовыми инструментами',
                'icon': '🐧',
            },
            {
                'id': PlaygroundSession.ENV_UBUNTU_NGINX,
                'label': 'Ubuntu 22.04 + nginx',
                'description': 'Ubuntu с предустановленным nginx',
                'icon': '🌐',
            },
            {
                'id': PlaygroundSession.ENV_ALPINE,
                'label': 'Alpine Linux',
                'description': 'Минималистичный Alpine (base образ)',
                'icon': '🏔️',
            },
        ]
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def playground_start_view(request):
    """
    Запустить Playground-сессию.
    Body: {environment: str}
    Создаёт PlaygroundSession на 30 минут.
    Возвращает session_id для WebSocket подключения.
    """
    environment = request.data.get('environment', PlaygroundSession.ENV_UBUNTU)

    valid_envs = [e[0] for e in PlaygroundSession.ENV_CHOICES]
    if environment not in valid_envs:
        return Response(
            {'error': f'Неверное окружение. Доступны: {valid_envs}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Останавливаем предыдущие активные playground сессии
    old_sessions = PlaygroundSession.objects.filter(
        user=request.user,
        status=PlaygroundSession.STATUS_ACTIVE,
    )
    for session in old_sessions:
        if session.container_id:
            try:
                from .docker_manager import DockerManager
                DockerManager().remove_container(session.container_id)
            except Exception as e:
                logger.warning(f'Не удалось удалить старый playground контейнер: {e}')
        session.status = PlaygroundSession.STATUS_STOPPED
        session.save(update_fields=['status'])

    # Создаём новую сессию
    session = PlaygroundSession.objects.create(
        user=request.user,
        environment=environment,
        expires_at=timezone.now() + timedelta(minutes=PLAYGROUND_DURATION_MINUTES),
    )

    logger.info(
        f'Playground сессия создана: пользователь={request.user.username}, '
        f'env={environment}, session={session.id}'
    )

    return Response({
        'session_id': session.id,
        'environment': environment,
        'environment_display': session.get_environment_display(),
        'expires_at': session.expires_at.isoformat(),
        'duration_minutes': PLAYGROUND_DURATION_MINUTES,
    }, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def playground_stop_view(request, session_id):
    """
    Досрочно остановить Playground-сессию.
    DELETE /api/playground/<session_id>/stop/
    """
    try:
        session = PlaygroundSession.objects.get(
            id=session_id,
            user=request.user,
            status=PlaygroundSession.STATUS_ACTIVE,
        )
    except PlaygroundSession.DoesNotExist:
        return Response(
            {'error': 'Сессия не найдена.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if session.container_id:
        try:
            from .docker_manager import DockerManager
            DockerManager().remove_container(session.container_id)
        except Exception as e:
            logger.warning(f'Не удалось удалить playground контейнер: {e}')

    session.status = PlaygroundSession.STATUS_STOPPED
    session.save(update_fields=['status'])

    return Response({'message': 'Playground остановлен.'})
