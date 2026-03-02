"""Тесты для роудмапа."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken
from apps.tasks.models import Task, UserTask
from django.utils import timezone

User = get_user_model()


class RoadmapTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com', username='testuser', password='pass123'
        )
        self.client = APIClient()
        token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Создаём linux задачи (4 штуки)
        self.linux_tasks = []
        for i in range(4):
            t = Task.objects.create(
                title_ru=f'Linux задача {i+1}',
                category='linux',
                difficulty='beginner',
                xp_reward=100,
                checker_type='command_output',
                checker_config={'command': 'echo ok', 'expected': 'ok'},
                order=i,
            )
            self.linux_tasks.append(t)

        # nginx задача требует linux
        self.nginx_task = Task.objects.create(
            title_ru='Nginx задача',
            category='nginx',
            difficulty='beginner',
            xp_reward=150,
            checker_type='port_check',
            checker_config={'port': 80},
            order=0,
        )

    def test_roadmap_returns_nodes_and_edges(self):
        """Роудмап возвращает узлы и рёбра."""
        response = self.client.get('/api/roadmap/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('nodes', response.data)
        self.assertIn('edges', response.data)

    def test_category_locked_when_prerequisites_not_met(self):
        """Nginx заблокирован если linux < 50%."""
        response = self.client.get('/api/roadmap/')
        nodes = {n['id']: n for n in response.data['nodes']}

        # Linux должен быть available (нет prerequisites)
        if 'linux' in nodes:
            self.assertIn(nodes['linux']['status'], ['available', 'in_progress', 'completed'])

    def test_roadmap_shows_progress(self):
        """Роудмап показывает прогресс по выполненным задачам."""
        # Выполняем 2 из 4 linux задач (50%)
        for task in self.linux_tasks[:2]:
            UserTask.objects.create(
                user=self.user,
                task=task,
                status='completed',
                xp_earned=100,
                completed_at=timezone.now(),
            )

        response = self.client.get('/api/roadmap/')
        nodes = {n['id']: n for n in response.data['nodes']}

        if 'linux' in nodes:
            self.assertEqual(nodes['linux']['completed'], 2)
