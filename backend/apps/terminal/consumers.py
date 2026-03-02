import json
import asyncio
import logging
import time
import re
import redis as redis_client
from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)

DANGEROUS_PATTERNS = [
    (r'rm\s+-rf\s+/', 'Осторожно! rm -rf / удалит ВСЮ файловую систему контейнера.'),
    (r'chmod\s+777', 'Осторожно! chmod 777 даёт права всем — это небезопасно.'),
    (r'dd\s+if=/dev/zero', 'Осторожно! dd if=/dev/zero может заполнить диск.'),
]

BLOCKED_PATTERNS = [
    (r':\(\)\{.*\}', 'Форк-бомба заблокирована.'),
]


class TerminalConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_id = None
        self.session = None
        self.exec_id = None
        self.exec_socket = None
        self.docker_manager = None
        self.read_task = None
        self.timer_task = None
        self.recording_start = None
        self.recording_events = []

    async def connect(self):
        user = self.scope.get('user')

        if not user or isinstance(user, AnonymousUser):
            await self.close(code=4001)
            return

        self.session_id = self.scope['url_route']['kwargs']['session_id']

        self.session = await self._get_session(user, self.session_id)
        if not self.session:
            logger.warning(f'Session {self.session_id} not found for user {user.id}')
            await self.close(code=4004)
            return

        if await database_sync_to_async(self.session.is_expired)():
            await self.close(code=4408)
            return

        await self.accept()

        try:
            from apps.terminal.docker_manager import DockerManager
            self.docker_manager = DockerManager()

            container_id = await database_sync_to_async(
                self.docker_manager.create_container
            )(self.session)

            await self._update_session_container(container_id)

            self.exec_id, self.exec_socket = await database_sync_to_async(
                self.docker_manager.get_exec_socket
            )(container_id)

            self.recording_start = time.time()

            await self._restore_history()

            self.read_task = asyncio.create_task(self._read_output())
            self.timer_task = asyncio.create_task(self._send_timer())

            logger.info(f'Terminal connected: user={user.id} session={self.session_id}')

        except Exception as e:
            logger.error(f'Terminal start error: {e}')
            await self.send(json.dumps({
                'type': 'error',
                'message': f'Не удалось запустить контейнер: {str(e)}',
            }))
            await self.close()

    async def disconnect(self, close_code):
        logger.info(f'Terminal disconnected: session={self.session_id} code={close_code}')

        for task in [self.read_task, self.timer_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        if self.exec_socket:
            try:
                self.exec_socket._sock.close()
            except Exception:
                pass

        if self.session:
            try:
                if self.recording_events:
                    await self._save_recording()

                if self.session.container_id:
                    await database_sync_to_async(
                        self.docker_manager.remove_container
                    )(self.session.container_id)

                await self._complete_session()

            except Exception as e:
                logger.error(f'Session cleanup error {self.session_id}: {e}')

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        msg_type = data.get('type')

        if msg_type == 'input':
            await self._handle_input(data.get('data', ''))
        elif msg_type == 'resize':
            await self._handle_resize(data.get('rows', 24), data.get('cols', 80))

    async def _handle_input(self, command: str) -> None:
        for pattern, message in BLOCKED_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                await self.send(json.dumps({'type': 'error', 'message': message}))
                return

        for pattern, message in DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                await self.send(json.dumps({'type': 'warning', 'message': message}))

        await self._save_to_history(command.strip())

        t = round(time.time() - self.recording_start, 6)
        self.recording_events.append([t, 'i', command])

        if self.exec_socket:
            try:
                self.exec_socket._sock.send(command.encode('utf-8'))
            except Exception as e:
                logger.error(f'Container send error: {e}')

    async def _handle_resize(self, rows: int, cols: int) -> None:
        if self.exec_id and self.docker_manager:
            try:
                await database_sync_to_async(
                    self.docker_manager.resize_terminal
                )(self.exec_id, rows, cols)
            except Exception as e:
                logger.warning(f'Resize error: {e}')

    async def _read_output(self) -> None:
        if not self.exec_socket:
            return

        loop = asyncio.get_event_loop()

        try:
            while True:
                try:
                    data = await loop.run_in_executor(None, self._read_socket_chunk)
                except Exception:
                    break

                if not data:
                    await asyncio.sleep(0.01)
                    continue

                output = data.decode('utf-8', errors='replace')

                t = round(time.time() - self.recording_start, 6)
                self.recording_events.append([t, 'o', output])

                await self.send(json.dumps({'type': 'output', 'data': output}))

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f'Container output read error: {e}')

    def _read_socket_chunk(self) -> bytes:
        try:
            self.exec_socket._sock.settimeout(0.1)
            return self.exec_socket._sock.recv(4096)
        except Exception:
            return b''

    async def _send_timer(self) -> None:
        try:
            while True:
                await asyncio.sleep(5)

                if not self.session:
                    break

                seconds_remaining = await database_sync_to_async(
                    self.session.time_remaining_seconds
                )()

                await self.send(json.dumps({
                    'type': 'timer',
                    'seconds_remaining': seconds_remaining,
                }))

                if seconds_remaining <= 0:
                    await self.send(json.dumps({
                        'type': 'expired',
                        'message': 'Время вышло! Сессия завершена.',
                    }))
                    await self.close()
                    break

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f'Timer error: {e}')

    async def _restore_history(self) -> None:
        try:
            r = redis_client.from_url(settings.REDIS_URL)
            history = r.lrange(f'terminal:{self.session_id}:history', 0, -1)
            if history:
                commands = [cmd.decode('utf-8') for cmd in reversed(history)]
                await self.send(json.dumps({'type': 'history', 'commands': commands}))
        except Exception as e:
            logger.debug(f'History restore failed: {e}')

    async def _save_to_history(self, command: str) -> None:
        if not command or command in ('', '\n', '\r'):
            return
        try:
            r = redis_client.from_url(settings.REDIS_URL)
            key = f'terminal:{self.session_id}:history'
            r.lpush(key, command)
            r.ltrim(key, 0, 99)
            r.expire(key, 86400)
        except Exception as e:
            logger.debug(f'History save failed: {e}')

    async def _save_recording(self) -> None:
        try:
            duration = time.time() - self.recording_start
            await database_sync_to_async(self._create_recording)(duration)
        except Exception as e:
            logger.error(f'Recording save error: {e}')

    def _create_recording(self, duration: float) -> None:
        from apps.terminal.models import SessionRecording

        SessionRecording.objects.update_or_create(
            session=self.session,
            defaults={
                'events_json': {
                    'version': 2,
                    'width': 80,
                    'height': 24,
                    'timestamp': int(self.recording_start),
                    'events': self.recording_events,
                },
                'duration_seconds': duration,
            },
        )

    @database_sync_to_async
    def _get_session(self, user, session_id: str):
        from apps.terminal.models import TerminalSession
        try:
            return TerminalSession.objects.select_related('task').get(
                id=session_id,
                user=user,
                status__in=['pending', 'active'],
            )
        except TerminalSession.DoesNotExist:
            return None

    @database_sync_to_async
    def _update_session_container(self, container_id: str) -> None:
        container_name = f'devops_task_{self.session.id}_{self.session.user_id}'
        self.session.container_id = container_id
        self.session.container_name = container_name
        self.session.status = 'active'
        self.session.save(update_fields=['container_id', 'container_name', 'status'])

    @database_sync_to_async
    def _complete_session(self) -> None:
        if self.session and self.session.status == 'active':
            self.session.status = 'completed'
            self.session.save(update_fields=['status'])
