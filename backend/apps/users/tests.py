"""
Тесты для приложения users: регистрация, логин, профили.
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    """Создаёт тестового пользователя."""
    user = User.objects.create_user(
        email='user@devops.ru',
        username='devopsuser',
        password='securepass123',
    )
    return user


@pytest.fixture
def auth_client(api_client, test_user):
    """API клиент с JWT авторизацией."""
    response = api_client.post(reverse('auth-login'), {
        'email': 'user@devops.ru',
        'password': 'securepass123',
    })
    token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client


class TestRegister:
    """Тесты регистрации пользователя."""

    def test_register_success(self, db, api_client):
        """Успешная регистрация нового пользователя."""
        response = api_client.post(reverse('auth-register'), {
            'email': 'newuser@devops.ru',
            'username': 'newuser',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
        assert User.objects.filter(email='newuser@devops.ru').exists()

    def test_register_duplicate_email(self, db, api_client, test_user):
        """Ошибка при регистрации с уже существующим email."""
        response = api_client.post(reverse('auth-register'), {
            'email': 'user@devops.ru',
            'username': 'anotheruser',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data

    def test_register_password_too_short(self, db, api_client):
        """Ошибка при коротком пароле."""
        response = api_client.post(reverse('auth-register'), {
            'email': 'test2@devops.ru',
            'username': 'testuser2',
            'password': '1234',
            'password_confirm': '1234',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_passwords_dont_match(self, db, api_client):
        """Ошибка если пароли не совпадают."""
        response = api_client.post(reverse('auth-register'), {
            'email': 'test3@devops.ru',
            'username': 'testuser3',
            'password': 'securepass123',
            'password_confirm': 'differentpass123',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestLogin:
    """Тесты входа в систему."""

    def test_login_success(self, db, api_client, test_user):
        """Успешный вход."""
        response = api_client.post(reverse('auth-login'), {
            'email': 'user@devops.ru',
            'password': 'securepass123',
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data

    def test_login_wrong_password(self, db, api_client, test_user):
        """Ошибка при неверном пароле."""
        response = api_client.post(reverse('auth-login'), {
            'email': 'user@devops.ru',
            'password': 'wrongpassword',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_nonexistent_email(self, db, api_client):
        """Ошибка при несуществующем email."""
        response = api_client.post(reverse('auth-login'), {
            'email': 'nobody@devops.ru',
            'password': 'somepassword',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestProfile:
    """Тесты профиля пользователя."""

    def test_get_profile_authenticated(self, db, auth_client, test_user):
        """Получение профиля авторизованного пользователя."""
        response = auth_client.get(reverse('user-me'))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == test_user.email
        assert 'xp' in response.data
        assert 'level' in response.data
        assert 'streak' in response.data
        assert 'xp_to_next_level' in response.data
        assert 'level_progress_pct' in response.data

    def test_get_profile_unauthenticated(self, db, api_client):
        """401 при запросе профиля без авторизации."""
        response = api_client.get(reverse('user-me'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile(self, db, auth_client, test_user):
        """Успешное обновление профиля."""
        response = auth_client.patch(reverse('user-me'), {
            'bio': 'DevOps энтузиаст',
        })
        assert response.status_code == status.HTTP_200_OK
        assert response.data['bio'] == 'DevOps энтузиаст'


class TestPublicProfile:
    """Тесты публичного профиля."""

    def test_public_profile_visible(self, db, api_client, test_user):
        """Публичный профиль виден всем."""
        test_user.is_public = True
        test_user.save()

        response = api_client.get(
            reverse('user-public-profile', kwargs={'username': test_user.username})
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == test_user.username

    def test_public_profile_hidden_when_private(self, db, api_client, test_user):
        """Приватный профиль возвращает 404."""
        test_user.is_public = False
        test_user.save()

        response = api_client.get(
            reverse('user-public-profile', kwargs={'username': test_user.username})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUserModel:
    """Тесты модели пользователя."""

    def test_add_xp_and_level_up(self, db):
        """Добавление XP и пересчёт уровня."""
        user = User.objects.create_user(
            email='xp@test.ru', username='xptester', password='pass12345'
        )
        assert user.level == User.LEVEL_BEGINNER

        user.add_xp(600)
        user.refresh_from_db()
        assert user.xp == 600
        assert user.level == User.LEVEL_JUNIOR

        user.add_xp(1500)
        user.refresh_from_db()
        assert user.level == User.LEVEL_MIDDLE

    def test_update_streak_new_user(self, db):
        """Стрик с нуля при первой активности."""
        user = User.objects.create_user(
            email='streak@test.ru', username='streaktester', password='pass12345'
        )
        user.update_streak()
        user.refresh_from_db()
        assert user.streak == 1

    def test_xp_to_next_level(self, db):
        """Расчёт XP до следующего уровня."""
        user = User.objects.create_user(
            email='next@test.ru', username='nexttester', password='pass12345'
        )
        user.xp = 200
        user.level = User.LEVEL_BEGINNER
        assert user.xp_to_next_level == 300  # 500 - 200

    def test_level_progress_pct(self, db):
        """Процент прогресса до следующего уровня."""
        user = User.objects.create_user(
            email='pct@test.ru', username='pcttester', password='pass12345'
        )
        user.xp = 250
        user.level = User.LEVEL_BEGINNER
        # 250 из 500 = 50%
        assert user.level_progress_pct == 50.0
