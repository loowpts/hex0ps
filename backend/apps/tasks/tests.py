"""
Тесты для задач: список, детали, подсказки, XP-формула, интеграция check-flow.
"""
import pytest
from unittest.mock import patch
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from apps.users.models import User
from apps.tasks.models import Task, UserTask
from apps.terminal.models import TerminalSession


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        email='taskuser@devops.ru',
        username='taskuser',
        password='securepass123',
    )


@pytest.fixture
def auth_client(api_client, test_user):
    response = api_client.post(reverse('auth-login'), {
        'email': 'taskuser@devops.ru',
        'password': 'securepass123',
    })
    token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client


@pytest.fixture
def sample_task(db):
    """Создаёт тестовую задачу."""
    return Task.objects.create(
        title_ru='Проверь порт Nginx',
        description_ru='Запусти Nginx и убедись что порт 80 открыт.',
        hint_1_ru='Попробуй команду systemctl',
        hint_2_ru='Используй systemctl start nginx',
        hint_3_ru='Выполни: systemctl start nginx && nc -z localhost 80',
        category='nginx',
        difficulty='beginner',
        task_type='regular',
        xp_reward=100,
        time_limit=30,
        docker_image='devops-platform/nginx:latest',
        checker_type='port_check',
        checker_config={'port': 80},
        solution_steps=[
            {'command': 'systemctl start nginx', 'explanation': 'Запускаем Nginx'},
        ],
    )


@pytest.fixture
def linux_task(db):
    return Task.objects.create(
        title_ru='Создай директорию',
        description_ru='Создай директорию /opt/devops.',
        hint_1_ru='Используй mkdir',
        hint_2_ru='mkdir -p /opt/devops',
        hint_3_ru='sudo mkdir -p /opt/devops',
        category='linux',
        difficulty='beginner',
        task_type='regular',
        xp_reward=50,
        time_limit=15,
        docker_image='devops-platform/base:latest',
        checker_type='file_exists',
        checker_config={'path': '/opt/devops'},
        solution_steps=[],
    )


class TestTaskList:
    """Тесты списка задач."""

    def test_get_tasks_list(self, db, api_client, sample_task, linux_task):
        """Список задач возвращается без авторизации."""
        response = api_client.get(reverse('task-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2

    def test_get_tasks_filter_by_category(self, db, api_client, sample_task, linux_task):
        """Фильтр по категории работает."""
        response = api_client.get(reverse('task-list'), {'category': 'nginx'})
        assert response.status_code == status.HTTP_200_OK
        for task in response.data:
            assert task['category'] == 'nginx'

    def test_get_tasks_filter_by_difficulty(self, db, api_client, sample_task, linux_task):
        """Фильтр по сложности работает."""
        response = api_client.get(reverse('task-list'), {'difficulty': 'beginner'})
        assert response.status_code == status.HTTP_200_OK
        for task in response.data:
            assert task['difficulty'] == 'beginner'

    def test_hints_not_in_list_response(self, db, api_client, sample_task):
        """Подсказки не включаются в список задач."""
        response = api_client.get(reverse('task-list'))
        assert response.status_code == status.HTTP_200_OK
        for task in response.data:
            assert 'hint_1_ru' not in task
            assert 'hint_2_ru' not in task
            assert 'hint_3_ru' not in task


class TestTaskDetail:
    """Тесты детальной информации о задаче."""

    def test_get_task_detail(self, db, api_client, sample_task):
        """Детальная страница задачи."""
        response = api_client.get(
            reverse('task-detail', kwargs={'task_id': sample_task.id})
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == sample_task.id
        assert response.data['title_ru'] == sample_task.title_ru

    def test_hints_not_in_detail_response(self, db, api_client, sample_task):
        """Подсказки не включаются в детали задачи."""
        response = api_client.get(
            reverse('task-detail', kwargs={'task_id': sample_task.id})
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'hint_1_ru' not in response.data
        assert 'hint_2_ru' not in response.data
        assert 'hint_3_ru' not in response.data

    def test_task_not_found(self, db, api_client):
        """404 для несуществующей задачи."""
        response = api_client.get(
            reverse('task-detail', kwargs={'task_id': 9999})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTaskHint:
    """Тесты системы подсказок."""

    def test_hint_endpoint_level1(self, db, auth_client, test_user, sample_task):
        """Получение первой подсказки."""
        # Сначала создаём UserTask
        UserTask.objects.create(
            user=test_user,
            task=sample_task,
            status='in_progress',
        )

        response = auth_client.post(
            reverse('task-hint', kwargs={'task_id': sample_task.id}),
            {'level': 1}
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'hint_text' in response.data
        assert response.data['hint_text'] == sample_task.hint_1_ru
        assert response.data['xp_multiplier'] == 1.0

    def test_hint_cannot_skip_level(self, db, auth_client, test_user, sample_task):
        """Нельзя пропустить уровень подсказки."""
        UserTask.objects.create(
            user=test_user,
            task=sample_task,
            status='in_progress',
            hints_used=0,
        )

        # Пытаемся получить сразу 3-ю подсказку
        response = auth_client.post(
            reverse('task-hint', kwargs={'task_id': sample_task.id}),
            {'level': 3}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_hint_level2_reduces_xp(self, db, auth_client, test_user, sample_task):
        """Подсказка 2 снижает XP до 75%."""
        UserTask.objects.create(
            user=test_user,
            task=sample_task,
            status='in_progress',
            hints_used=1,  # Уже открыта 1-я
        )

        response = auth_client.post(
            reverse('task-hint', kwargs={'task_id': sample_task.id}),
            {'level': 2}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['xp_multiplier'] == 0.75

    def test_hint_level3_reduces_xp(self, db, auth_client, test_user, sample_task):
        """Подсказка 3 снижает XP до 50%."""
        UserTask.objects.create(
            user=test_user,
            task=sample_task,
            status='in_progress',
            hints_used=2,  # Открыты 1 и 2
        )

        response = auth_client.post(
            reverse('task-hint', kwargs={'task_id': sample_task.id}),
            {'level': 3}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['xp_multiplier'] == 0.5

    def test_hint_requires_auth(self, db, api_client, sample_task):
        """Подсказка требует авторизации."""
        response = api_client.post(
            reverse('task-hint', kwargs={'task_id': sample_task.id}),
            {'level': 1}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ─── XP Multiplier: модельный метод ───────────────────────────────────────────

class TestXpMultiplierModel:
    """Parametrized тесты для UserTask.calculate_xp_multiplier()."""

    @pytest.mark.parametrize("hints_used,expected", [
        (0, 1.0),   # подсказок нет — базовый множитель
        (1, 1.0),   # подсказка 1 бесплатна
        (2, 0.75),  # подсказка 2 → -25% XP
        (3, 0.50),  # подсказка 3 → -50% XP
        (5, 0.50),  # hints_used > 3 зажимается до 3
    ])
    def test_calculate_xp_multiplier(self, db, test_user, sample_task, hints_used, expected):
        ut = UserTask(user=test_user, task=sample_task, hints_used=hints_used)
        assert ut.calculate_xp_multiplier() == expected


# ─── XP Formula: полная формула начисления ────────────────────────────────────

class TestXpFormula:
    """
    Parametrized тесты для полной формулы XP из task_check_view.

    Формула: base_multiplier * (1.10 если нет подсказок) * (1.15 если стрик ≥ 7)
    """

    @pytest.mark.parametrize("hints_used,streak,xp_reward,expected_xp", [
        (0, 0,  100, 110),  # нет подсказок: 100 * 1.0 * 1.10 = 110
        (0, 7,  100, 126),  # нет подсказок + стрик: 100 * 1.0 * 1.10 * 1.15 = 126.5 → 126
        (1, 0,  100, 100),  # подсказка 1 бесплатна, бонуса нет
        (2, 0,  100,  75),  # подсказка 2: 100 * 0.75 = 75
        (3, 0,  100,  50),  # подсказка 3: 100 * 0.50 = 50
        (2, 7,  200, 172),  # подсказка 2 + стрик: 200 * 0.75 * 1.15 = 172.5 → 172
    ])
    def test_xp_formula(self, hints_used, streak, xp_reward, expected_xp):
        from apps.tasks.constants import (
            XP_HINT_MULTIPLIERS, XP_BONUS_NO_HINTS,
            XP_BONUS_STREAK, STREAK_BONUS_THRESHOLD,
        )
        multiplier = XP_HINT_MULTIPLIERS[min(hints_used, 3)]
        if hints_used == 0:
            multiplier *= XP_BONUS_NO_HINTS
        if streak >= STREAK_BONUS_THRESHOLD:
            multiplier *= XP_BONUS_STREAK
        assert int(xp_reward * multiplier) == expected_xp


# ─── Integration: полный flow start → check → XP ─────────────────────────────

class TestTaskCheckIntegration:
    """
    Интеграционные тесты flow: checker → XP → UserTask.
    Docker и внешние сервисы мокируются.
    """

    @pytest.fixture
    def active_session(self, db, test_user, sample_task):
        """Создаёт активную сессию и UserTask in_progress."""
        UserTask.objects.create(
            user=test_user,
            task=sample_task,
            status='in_progress',
            started_at=timezone.now(),
        )
        return TerminalSession.objects.create(
            user=test_user,
            task=sample_task,
            status='active',
            container_id='test-container-abc',
            expires_at=timezone.now() + timezone.timedelta(minutes=30),
        )

    def test_successful_check_awards_xp(self, db, auth_client, test_user, sample_task, active_session):
        """Успешная проверка → UserTask.completed, xp_earned > 0."""
        with patch('apps.tasks.checker.run_checker', return_value=(True, 'OK')), \
             patch('apps.users.achievements.check_and_award_achievements', return_value=[]), \
             patch('apps.tasks.views._check_category_certificate', return_value=None), \
             patch('apps.terminal.tasks.remove_container_async'):
            response = auth_client.post(
                reverse('task-check', kwargs={'task_id': sample_task.id})
            )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['xp_earned'] > 0

        user_task = UserTask.objects.get(user=test_user, task=sample_task)
        assert user_task.status == 'completed'
        assert user_task.xp_earned > 0
        assert user_task.completed_at is not None

    def test_failed_check_keeps_in_progress(self, db, auth_client, test_user, sample_task, active_session):
        """Неуспешная проверка не меняет статус UserTask."""
        with patch('apps.tasks.checker.run_checker', return_value=(False, 'Port closed')):
            response = auth_client.post(
                reverse('task-check', kwargs={'task_id': sample_task.id})
            )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is False

        user_task = UserTask.objects.get(user=test_user, task=sample_task)
        assert user_task.status == 'in_progress'
        assert user_task.xp_earned == 0

    def test_no_session_returns_400(self, db, auth_client, sample_task):
        """Без активной сессии — 400."""
        response = auth_client.post(
            reverse('task-check', kwargs={'task_id': sample_task.id})
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_second_completion_no_double_xp(self, db, auth_client, test_user, sample_task, active_session):
        """Повторная успешная проверка не начисляет XP дважды."""
        with patch('apps.tasks.checker.run_checker', return_value=(True, 'OK')), \
             patch('apps.users.achievements.check_and_award_achievements', return_value=[]), \
             patch('apps.tasks.views._check_category_certificate', return_value=None), \
             patch('apps.terminal.tasks.remove_container_async'):
            # Первая проверка — XP начисляется
            auth_client.post(reverse('task-check', kwargs={'task_id': sample_task.id}))
            xp_after_first = User.objects.get(pk=test_user.pk).xp

            # Сбрасываем сессию для повторной проверки
            active_session.status = 'active'
            active_session.save(update_fields=['status'])

            # Вторая проверка — XP не должен начисляться снова
            auth_client.post(reverse('task-check', kwargs={'task_id': sample_task.id}))
            xp_after_second = User.objects.get(pk=test_user.pk).xp

        assert xp_after_second == xp_after_first
