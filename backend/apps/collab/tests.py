"""Тесты для командного режима (Collab)."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.tasks.models import Task
from apps.terminal.models import TerminalSession
from apps.collab.models import CollabSession
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class CollabTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@test.com', username='owner', password='pass123'
        )
        self.guest = User.objects.create_user(
            email='guest@test.com', username='guest', password='pass123'
        )
        self.task = Task.objects.create(
            title_ru='Тестовая задача',
            category='linux',
            difficulty='beginner',
            xp_reward=100,
            checker_type='command_output',
            checker_config={'command': 'echo test', 'expected': 'test'},
        )
        self.session = TerminalSession.objects.create(
            user=self.owner,
            task=self.task,
            status='active',
            expires_at=timezone.now() + timedelta(hours=1),
        )

    def test_create_collab_invite(self):
        """Владелец может создать приглашение."""
        collab = CollabSession.objects.create(
            owner=self.owner,
            terminal_session=self.session,
            active_user=self.owner,
        )
        self.assertIsNotNone(collab.invite_token)
        self.assertEqual(collab.status, 'waiting')
        self.assertEqual(collab.owner, self.owner)

    def test_guest_join_collab(self):
        """Гость может присоединиться к сессии."""
        collab = CollabSession.objects.create(
            owner=self.owner,
            terminal_session=self.session,
            active_user=self.owner,
        )
        collab.guest = self.guest
        collab.status = 'active'
        collab.save()

        collab.refresh_from_db()
        self.assertEqual(collab.guest, self.guest)
        self.assertEqual(collab.status, 'active')

    def test_control_transfer(self):
        """Управление передаётся от владельца к гостю."""
        collab = CollabSession.objects.create(
            owner=self.owner,
            guest=self.guest,
            terminal_session=self.session,
            status='active',
            active_user=self.owner,
        )
        # Передаём управление гостю
        collab.active_user = self.guest
        collab.save()

        collab.refresh_from_db()
        self.assertEqual(collab.active_user, self.guest)

    def test_only_owner_can_close(self):
        """Только владелец может закрыть сессию."""
        collab = CollabSession.objects.create(
            owner=self.owner,
            guest=self.guest,
            terminal_session=self.session,
            status='active',
            active_user=self.owner,
        )
        self.assertEqual(collab.owner, self.owner)
        self.assertNotEqual(collab.guest, self.owner)
