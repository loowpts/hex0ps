"""
View страницы статуса сервисов.
"""
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def check_db_connection() -> bool:
    try:
        from django.db import connection
        connection.ensure_connection()
        return True
    except Exception as e:
        logger.warning(f'DB health check failed: {e}')
        return False


def check_redis_connection() -> bool:
    try:
        import redis as redis_client
        from django.conf import settings
        r = redis_client.from_url(settings.REDIS_URL)
        r.ping()
        return True
    except Exception as e:
        logger.warning(f'Redis health check failed: {e}')
        return False


def check_ollama_health() -> bool:
    try:
        import requests
        from django.conf import settings
        resp = requests.get(f'{settings.OLLAMA_URL}/api/tags', timeout=3)
        return resp.status_code == 200
    except Exception as e:
        logger.warning(f'Ollama health check failed: {e}')
        return False


def check_channels_health() -> bool:
    """Проверка Redis через channel layer."""
    try:
        from channels.layers import get_channel_layer
        layer = get_channel_layer()
        return layer is not None
    except Exception as e:
        logger.warning(f'Channels health check failed: {e}')
        return False


@api_view(['GET'])
@permission_classes([AllowAny])
def status_view(request):
    """
    Статус всех сервисов платформы.
    Используется страницей /status во фронтенде.
    """
    checks = {
        'api': True,
        'database': check_db_connection(),
        'redis': check_redis_connection(),
        'websocket': check_channels_health(),
        'ai': check_ollama_health(),
    }

    overall = all(checks.values())

    return Response({
        'status': 'ok' if overall else 'degraded',
        'services': {
            'api': {'status': 'ok', 'name': 'API'},
            'database': {'status': 'ok' if checks['database'] else 'error', 'name': 'База данных'},
            'redis': {'status': 'ok' if checks['redis'] else 'error', 'name': 'Redis'},
            'websocket': {'status': 'ok' if checks['websocket'] else 'error', 'name': 'WebSocket'},
            'ai': {'status': 'ok' if checks['ai'] else 'error', 'name': 'AI (Ollama)'},
        }
    })
