"""
WebSocket consumer для Playground — свободного терминала.
Аналог TerminalConsumer но без задачи, чекера и записи.
"""
import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)

PLAYGROUND_DURATION = 30 * 60  # 30 минут в секундах


class PlaygroundConsumer(AsyncWebsocketConsumer):
    """
    WebSocket Consumer для Playground.

    Протокол идентичен TerminalConsumer:
    Клиент → Сервер:
      {"type": "input", "data": "команда\\n"}
      {"type": "resize", "rows": 24, "cols": 80}

    Сервер → Клиент:
      {"type": "output", "data": "вывод"}
      {"type": "error", "message": "ошибка"}
      {"type": "timer", "seconds_remaining": 120}
      {"type": "expired", "message": "Время вышло"}
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_id = None
        self.session = None
        self.exec_id = None
        self.exec_socket = None
        self.docker_manager = None
        self.read_task = None
        self.timer_task = None

    async def connect(self):
        user = self.scope.get('user')

        if not user or isinstance(user, AnonymousUser):
            await self.close(code=4001)
            return

        self.session_id = self.scope['url_route']['kwargs']['session_id']

        self.session = await self._get_session(user, self.session_id)
        if not self.session:
            await self.close(code=4004)
            return

        if await database_sync_to_async(self.session.is_expired)():
            await self.close(code=4408)
            return

        await self.accept()

        try:
            from apps.terminal.docker_manager import DockerManager
            self.docker_manager = DockerManager()

            # Создаём контейнер для playground
            container_id = await database_sync_to_async(
                self._create_playground_container
            )()

            await database_sync_to_async(self._update_container)(container_id)

            self.exec_id, self.exec_socket = await database_sync_to_async(
                self.docker_manager.get_exec_socket
            )(container_id)

            self.read_task = asyncio.create_task(self._read_output())
            self.timer_task = asyncio.create_task(self._send_timer())

            logger.info(
                f'Playground подключён: пользователь={user.username}, '
                f'сессия={self.session_id}, контейнер={container_id[:12]}'
            )

        except Exception as e:
            logger.error(f'Ошибка запуска playground: {e}')
            await self.send(json.dumps({
                'type': 'error',
                'message': f'Не удалось запустить контейнер: {str(e)}'
            }))
            await self.close()

    def _create_playground_container(self):
        """Создаёт Docker-контейнер для playground (синхронно)."""
        container_name = f'devops_playground_{self.session.id}_{self.session.user_id}'
        import docker
        from django.conf import settings
        client = docker.from_env()
        container = client.containers.run(
            image=self.session.docker_image,
            name=container_name,
            mem_limit=settings.DOCKER_SANDBOX_MEMORY_LIMIT,
            cpu_quota=settings.DOCKER_SANDBOX_CPU_QUOTA,
            network=settings.DOCKER_SANDBOX_NETWORK,
            user='devops',
            detach=True,
            tty=True,
            stdin_open=True,
            remove=False,
            privileged=False,
            cap_drop=['ALL'],
            security_opt=['no-new-privileges:true'],
            environment={
                'TERM': 'xterm-256color',
                'LANG': 'en_US.UTF-8',
                'HOME': '/home/devops',
            },
            tmpfs={'/tmp': 'size=64m'},
            working_dir='/home/devops',
        )
        return container.id

    def _update_container(self, container_id: str):
        from .models import PlaygroundSession
        PlaygroundSession.objects.filter(pk=self.session.pk).update(container_id=container_id)
        self.session.container_id = container_id

    async def disconnect(self, close_code):
        logger.info(f'Playground отключён: сессия={self.session_id}, код={close_code}')

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

        if self.session and self.session.container_id:
            try:
                if self.docker_manager:
                    await database_sync_to_async(
                        self.docker_manager.remove_container
                    )(self.session.container_id)
            except Exception as e:
                logger.error(f'Ошибка удаления playground контейнера: {e}')

        # Обновляем статус
        if self.session:
            await database_sync_to_async(self._mark_expired)()

    def _mark_expired(self):
        from .models import PlaygroundSession
        PlaygroundSession.objects.filter(pk=self.session.pk).update(
            status=PlaygroundSession.STATUS_EXPIRED
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        msg_type = data.get('type')

        if msg_type == 'input' and self.exec_socket:
            input_data = data.get('data', '')
            if input_data:
                try:
                    self.exec_socket._sock.send(input_data.encode('utf-8'))
                except Exception as e:
                    logger.error(f'Ошибка отправки в playground контейнер: {e}')

        elif msg_type == 'resize' and self.exec_id and self.docker_manager:
            rows = data.get('rows', 24)
            cols = data.get('cols', 80)
            try:
                await database_sync_to_async(self.docker_manager.resize_terminal)(
                    self.exec_id, rows, cols
                )
            except Exception:
                pass

    async def _read_output(self):
        """Читает вывод из контейнера и отправляет клиенту."""
        try:
            while True:
                chunk = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.exec_socket._sock.recv(4096)
                )
                if not chunk:
                    break
                output = chunk.decode('utf-8', errors='replace')
                await self.send(json.dumps({'type': 'output', 'data': output}))
        except Exception as e:
            logger.debug(f'Playground output loop завершён: {e}')
            await self.close()

    async def _send_timer(self):
        """Периодически отправляет таймер, закрывает по истечении."""
        try:
            while True:
                await asyncio.sleep(30)
                remaining = await database_sync_to_async(
                    self.session.time_remaining_seconds
                )()
                await self.send(json.dumps({
                    'type': 'timer',
                    'seconds_remaining': remaining,
                }))
                if remaining <= 0:
                    await self.send(json.dumps({
                        'type': 'expired',
                        'message': 'Время playground истекло. Сессия завершена.',
                    }))
                    await self.close()
                    break
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f'Ошибка таймера playground: {e}')

    @database_sync_to_async
    def _get_session(self, user, session_id):
        from .models import PlaygroundSession
        try:
            return PlaygroundSession.objects.get(
                id=session_id,
                user=user,
                status=PlaygroundSession.STATUS_ACTIVE,
            )
        except PlaygroundSession.DoesNotExist:
            return None
