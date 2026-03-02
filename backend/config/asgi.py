"""
ASGI конфигурация для DevOps Learning Platform.
Поддерживает HTTP и WebSocket через Django Channels.
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

# Инициализируем Django до импорта роутеров
django_asgi_app = get_asgi_application()

from config.routing import websocket_urlpatterns  # noqa: E402
from apps.terminal.middleware import JWTAuthMiddleware  # noqa: E402

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
