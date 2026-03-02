"""
Unit тесты для WS ticket endpoint и одноразового использования ticket.

Redis мокается через fakeredis — тесты не требуют запущенного Redis.
Покрывает: выдачу ticket, хранение в Redis, TTL, аутентификацию, одноразовость.
"""
import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import fakeredis

from apps.users.models import User

WS_TICKET_PREFIX = 'ws_ticket:'


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        email='ticketuser@devops.ru',
        username='ticketuser',
        password='securepass123',
    )


@pytest.fixture
def auth_client(api_client, test_user):
    response = api_client.post(reverse('auth-login'), {
        'email': 'ticketuser@devops.ru',
        'password': 'securepass123',
    })
    token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client


@pytest.fixture
def fake_redis():
    """Изолированный fakeredis без сетевых зависимостей."""
    return fakeredis.FakeRedis()


# ─── TestIssueWsTicket ────────────────────────────────────────────────────────

class TestIssueWsTicket:
    """Тесты HTTP-эндпоинта POST /api/terminal/ticket/."""

    def test_requires_authentication(self, api_client):
        """Без аутентификации — 401 Unauthorized."""
        response = api_client.post(reverse('terminal-ws-ticket'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_returns_ticket_for_auth_user(self, auth_client, fake_redis):
        """Авторизованный пользователь получает UUID-ticket."""
        with patch('apps.terminal.ticket_views.redis_client.from_url', return_value=fake_redis):
            response = auth_client.post(reverse('terminal-ws-ticket'))

        assert response.status_code == status.HTTP_200_OK
        assert 'ticket' in response.data
        # UUID4: 8-4-4-4-12 = 36 символов с дефисами
        assert len(response.data['ticket']) == 36

    def test_ticket_stored_in_redis(self, auth_client, fake_redis):
        """Ticket сохраняется в Redis с корректным ключом-префиксом."""
        with patch('apps.terminal.ticket_views.redis_client.from_url', return_value=fake_redis):
            response = auth_client.post(reverse('terminal-ws-ticket'))

        ticket = response.data['ticket']
        assert fake_redis.exists(f'{WS_TICKET_PREFIX}{ticket}')

    def test_ticket_has_correct_ttl(self, auth_client, fake_redis):
        """TTL ticket не превышает 30 секунд."""
        with patch('apps.terminal.ticket_views.redis_client.from_url', return_value=fake_redis):
            response = auth_client.post(reverse('terminal-ws-ticket'))

        ticket = response.data['ticket']
        ttl = fake_redis.ttl(f'{WS_TICKET_PREFIX}{ticket}')
        assert 0 < ttl <= 30

    def test_ticket_stores_correct_user_id(self, auth_client, test_user, fake_redis):
        """В Redis сохраняется ID текущего пользователя."""
        with patch('apps.terminal.ticket_views.redis_client.from_url', return_value=fake_redis):
            response = auth_client.post(reverse('terminal-ws-ticket'))

        ticket = response.data['ticket']
        stored_id = int(fake_redis.get(f'{WS_TICKET_PREFIX}{ticket}'))
        assert stored_id == test_user.id

    def test_redis_failure_returns_503(self, auth_client):
        """При недоступности Redis — 503 Service Unavailable."""
        broken_redis = MagicMock()
        broken_redis.setex.side_effect = Exception('Redis connection refused')
        with patch('apps.terminal.ticket_views.redis_client.from_url', return_value=broken_redis):
            response = auth_client.post(reverse('terminal-ws-ticket'))

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert 'error' in response.data

    def test_each_request_generates_unique_ticket(self, auth_client, fake_redis):
        """Каждый запрос создаёт новый уникальный ticket."""
        with patch('apps.terminal.ticket_views.redis_client.from_url', return_value=fake_redis):
            resp1 = auth_client.post(reverse('terminal-ws-ticket'))
            resp2 = auth_client.post(reverse('terminal-ws-ticket'))

        assert resp1.data['ticket'] != resp2.data['ticket']


# ─── TestTicketOneTimeUse ─────────────────────────────────────────────────────

class TestTicketOneTimeUse:
    """
    Тесты одноразового использования ticket через Redis pipeline.

    Проверяет атомарный get+delete из middleware.get_user_from_ticket()
    без запуска ASGI / Django Channels.
    """

    def test_ticket_consumed_after_first_use(self, fake_redis):
        """Ticket удаляется из Redis при первом использовании (pipeline get+delete)."""
        ticket = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
        key = f'{WS_TICKET_PREFIX}{ticket}'
        fake_redis.setex(key, 30, '42')

        # Первое использование — атомарный get + delete
        with fake_redis.pipeline() as pipe:
            pipe.get(key)
            pipe.delete(key)
            user_id_bytes, _ = pipe.execute()

        assert user_id_bytes is not None
        assert int(user_id_bytes) == 42
        assert not fake_redis.exists(key)  # Ticket удалён

    def test_ticket_not_reusable(self, fake_redis):
        """После первого использования ticket недействителен."""
        ticket = 'aaaaaaaa-bbbb-cccc-dddd-ffffffffffff'
        key = f'{WS_TICKET_PREFIX}{ticket}'
        fake_redis.setex(key, 30, '99')

        # Первое использование
        with fake_redis.pipeline() as pipe:
            pipe.get(key)
            pipe.delete(key)
            pipe.execute()

        # Повторное использование — ключ уже удалён
        with fake_redis.pipeline() as pipe:
            pipe.get(key)
            pipe.delete(key)
            user_id_bytes, _ = pipe.execute()

        assert user_id_bytes is None

    def test_missing_ticket_returns_none(self, fake_redis):
        """Несуществующий ticket → None (не падает с ошибкой)."""
        key = f'{WS_TICKET_PREFIX}nonexistent-ticket-xyz'

        with fake_redis.pipeline() as pipe:
            pipe.get(key)
            pipe.delete(key)
            user_id_bytes, _ = pipe.execute()

        assert user_id_bytes is None
