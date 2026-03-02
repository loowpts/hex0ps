"""
JWT Middleware для аутентификации WebSocket соединений.

Поддерживает два метода аутентификации:
  1. ?ticket=<uuid>  — одноразовый ticket из Redis (рекомендуется, не попадает в логи)
  2. ?token=<jwt>    — JWT access token (fallback для обратной совместимости)
"""
import logging
from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

logger = logging.getLogger(__name__)

WS_TICKET_PREFIX = 'ws_ticket:'


@database_sync_to_async
def get_user_from_ticket(ticket: str):
    """
    Проверяет одноразовый ticket в Redis.
    Ticket удаляется при первом использовании (atomic get+delete через pipeline).
    """
    from django.contrib.auth import get_user_model
    from django.conf import settings
    import redis as redis_client

    User = get_user_model()
    key = f'{WS_TICKET_PREFIX}{ticket}'

    try:
        r = redis_client.from_url(settings.REDIS_URL)
        # Атомарный get + delete через pipeline — ticket нельзя использовать дважды
        with r.pipeline() as pipe:
            pipe.get(key)
            pipe.delete(key)
            user_id_bytes, _ = pipe.execute()

        if not user_id_bytes:
            logger.debug('WS ticket не найден или уже использован')
            return AnonymousUser()

        user_id = int(user_id_bytes)
        user = User.objects.get(id=user_id, is_active=True)
        return user
    except User.DoesNotExist:
        logger.debug('Пользователь из WS ticket не найден')
        return AnonymousUser()
    except Exception as e:
        logger.error(f'Ошибка аутентификации по WS ticket: {e}')
        return AnonymousUser()


@database_sync_to_async
def get_user_from_token(token_key: str):
    """
    Декодирует JWT и возвращает пользователя.
    При ошибке возвращает AnonymousUser.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        token = AccessToken(token_key)
        user_id = token['user_id']
        user = User.objects.get(id=user_id, is_active=True)
        return user
    except (TokenError, InvalidToken):
        logger.debug('Невалидный JWT токен в WebSocket запросе')
        return AnonymousUser()
    except User.DoesNotExist:
        logger.debug('Пользователь из JWT не найден')
        return AnonymousUser()
    except Exception as e:
        logger.error(f'Ошибка JWT аутентификации WebSocket: {e}')
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    Middleware для аутентификации WebSocket соединений.

    Порядок проверки:
      1. ?ticket=<uuid>  — одноразовый Redis ticket (предпочтительно)
      2. ?token=<jwt>    — JWT в URL (fallback)
    """

    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        params = parse_qs(query_string)

        ticket = params.get('ticket', [None])[0]
        token_key = params.get('token', [None])[0]

        if ticket:
            scope['user'] = await get_user_from_ticket(ticket)
        elif token_key:
            scope['user'] = await get_user_from_token(token_key)
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)
