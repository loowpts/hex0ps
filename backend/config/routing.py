"""
WebSocket маршруты для Django Channels.
"""
from django.urls import path
from apps.terminal.consumers import TerminalConsumer
from apps.terminal.playground_consumer import PlaygroundConsumer
from apps.collab.consumers import CollabConsumer

websocket_urlpatterns = [
    # Терминальная сессия
    path('ws/terminal/<str:session_id>/', TerminalConsumer.as_asgi()),
    # Playground
    path('ws/playground/<str:session_id>/', PlaygroundConsumer.as_asgi()),
    # Командный режим
    path('ws/collab/<str:session_id>/', CollabConsumer.as_asgi()),
]
