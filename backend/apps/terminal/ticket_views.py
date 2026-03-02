"""
Одноразовый ticket для WebSocket аутентификации.

Вместо передачи JWT-токена в URL (который логируется в браузере и proxy),
клиент получает короткоживущий UUID-ticket через защищённый HTTP-запрос.
Ticket используется ровно один раз и удаляется из Redis при проверке.
"""
import uuid
import logging

import redis as redis_client
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

WS_TICKET_PREFIX = 'ws_ticket:'
WS_TICKET_TTL = 30  # секунды


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def issue_ws_ticket(request):
    """
    Выдаёт одноразовый ticket для открытия WebSocket.

    Ticket действителен 30 секунд и уничтожается при первом использовании.
    Клиент открывает ws://.../?ticket=<uuid> вместо ?token=<jwt>.
    """
    ticket = str(uuid.uuid4())
    key = f'{WS_TICKET_PREFIX}{ticket}'

    try:
        r = redis_client.from_url(settings.REDIS_URL)
        r.setex(key, WS_TICKET_TTL, str(request.user.id))
    except Exception as e:
        logger.error(f'Ошибка создания WS ticket для пользователя {request.user.id}: {e}')
        return Response(
            {'error': 'Не удалось создать ticket. Попробуй ещё раз.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return Response({'ticket': ticket})
