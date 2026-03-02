"""Тесты для записей терминальных сессий."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.tasks.models import Task
from apps.terminal.models import TerminalSession, SessionRecording
from apps.terminal.session_recorder import SessionRecorder
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class RecordingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com', username='testuser', password='pass123'
        )
        self.task = Task.objects.create(
            title_ru='Тестовая задача',
            category='linux',
            difficulty='beginner',
            xp_reward=100,
            checker_type='command_output',
            checker_config={'command': 'echo hi', 'expected': 'hi'},
        )
        self.session = TerminalSession.objects.create(
            user=self.user,
            task=self.task,
            status='completed',
            expires_at=timezone.now() + timedelta(hours=1),
        )

    def test_session_recorder_records_events(self):
        """SessionRecorder правильно записывает события."""
        recorder = SessionRecorder(self.session.id, cols=80, rows=24)
        recorder.record_output('$ ')
        recorder.record_input('ls -la\n')
        recorder.record_output('total 8\n')

        asciinema = recorder.to_asciinema_json()
        self.assertEqual(asciinema['version'], 2)
        self.assertEqual(asciinema['width'], 80)
        self.assertEqual(asciinema['height'], 24)
        self.assertEqual(len(asciinema['events']), 3)
        self.assertEqual(asciinema['events'][1][1], 'i')
        self.assertEqual(asciinema['events'][2][1], 'o')

    def test_recording_saved_after_session(self):
        """Запись сохраняется в БД через SessionRecorder.save()."""
        recorder = SessionRecorder(self.session.id, cols=80, rows=24)
        recorder.record_output('Hello World\n')

        share_id = recorder.save()
        self.assertIsNotNone(share_id)

        recording = SessionRecording.objects.get(share_id=share_id)
        self.assertEqual(recording.session, self.session)
        self.assertFalse(recording.is_public)

    def test_public_replay_accessible_without_auth(self):
        """Публичная запись доступна без авторизации."""
        recording = SessionRecording.objects.create(
            session=self.session,
            events_json={'version': 2, 'width': 80, 'height': 24, 'events': []},
            cols=80,
            rows=24,
            duration_seconds=10.0,
            is_public=True,
        )

        client = APIClient()
        response = client.get(f'/api/recordings/{recording.share_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_public'])

    def test_private_replay_requires_auth(self):
        """Приватная запись требует авторизации."""
        recording = SessionRecording.objects.create(
            session=self.session,
            events_json={'version': 2, 'width': 80, 'height': 24, 'events': []},
            cols=80,
            rows=24,
            duration_seconds=5.0,
            is_public=False,
        )

        client = APIClient()
        response = client.get(f'/api/recordings/{recording.share_id}/')
        self.assertEqual(response.status_code, 403)
