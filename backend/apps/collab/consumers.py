"""
WebSocket consumer для командного режима (Collab).
Два пользователя в одном терминале.
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)


class CollabConsumer(AsyncWebsocketConsumer):
    """
    Протокол:
    - owner и guest подключаются к одной channel group
    - Только active_user может отправлять input в терминал
    - Оба получают output

    Сервер → Клиент:
      {"type": "user_joined", "username": "..."}
      {"type": "control_transferred", "to": "username"}
      {"type": "output", "data": "..."}
      {"type": "error", "message": "..."}

    Клиент → Сервер:
      {"type": "input", "data": "команда"}
      {"type": "transfer_control"}
      {"type": "request_control"}
    """

    async def connect(self):
        user = self.scope.get('user')

        if not user or isinstance(user, AnonymousUser):
            await self.close(code=4001)
            return

        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.group_name = f'collab_{self.session_id}'

        # Загружаем CollabSession
        self.collab_session = await self._get_collab_session(self.session_id)
        if not self.collab_session:
            await self.close(code=4004)
            return

        # Определяем роль пользователя
        self.is_owner = (self.collab_session.owner_id == user.id)
        self.is_guest = (self.collab_session.guest_id == user.id)

        if not self.is_owner and not self.is_guest:
            await self.close(code=4003)
            return

        # Присоединяемся к group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Уведомляем всех что пользователь подключился
        await self.channel_layer.group_send(self.group_name, {
            'type': 'collab_user_joined',
            'username': user.username,
            'role': 'owner' if self.is_owner else 'guest',
        })

        # Если гость — обновляем статус сессии
        if self.is_guest:
            await self._activate_collab_session()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        user = self.scope['user']
        msg_type = data.get('type')

        if msg_type == 'input':
            # Только active_user может вводить команды
            active_user_id = await self._get_active_user_id()
            if active_user_id != user.id:
                await self.send(json.dumps({
                    'type': 'error',
                    'message': 'Сейчас не твоя очередь. Управляет другой участник.'
                }))
                return

            # Пересылаем в terminal consumer через terminal session
            await self.channel_layer.group_send(self.group_name, {
                'type': 'collab_input',
                'data': data.get('data', ''),
                'username': user.username,
            })

        elif msg_type == 'transfer_control':
            # Владелец передаёт управление
            if not self.is_owner:
                return
            collab = await self._get_collab_session(self.session_id)
            if collab and collab.guest:
                await self._transfer_control(collab.guest_id)
                await self.channel_layer.group_send(self.group_name, {
                    'type': 'collab_control_transferred',
                    'to': collab.guest.username if collab.guest else '',
                })

        elif msg_type == 'request_control':
            # Гость запрашивает управление
            await self.channel_layer.group_send(self.group_name, {
                'type': 'collab_control_requested',
                'username': user.username,
            })

    # Channel layer event handlers

    async def collab_user_joined(self, event):
        await self.send(json.dumps({
            'type': 'user_joined',
            'username': event['username'],
            'role': event['role'],
        }))

    async def collab_input(self, event):
        """Получаем ввод — пересылаем в терминал."""
        # Реализация через terminal session WebSocket
        pass

    async def collab_control_transferred(self, event):
        await self.send(json.dumps({
            'type': 'control_transferred',
            'to': event['to'],
        }))

    async def collab_control_requested(self, event):
        await self.send(json.dumps({
            'type': 'control_requested',
            'username': event['username'],
        }))

    @database_sync_to_async
    def _get_collab_session(self, session_id: str):
        from apps.collab.models import CollabSession
        try:
            return CollabSession.objects.select_related(
                'owner', 'guest', 'active_user', 'terminal_session'
            ).get(id=session_id)
        except CollabSession.DoesNotExist:
            return None

    @database_sync_to_async
    def _activate_collab_session(self):
        from apps.collab.models import CollabSession
        CollabSession.objects.filter(id=self.session_id).update(status='active')

    @database_sync_to_async
    def _get_active_user_id(self):
        from apps.collab.models import CollabSession
        try:
            s = CollabSession.objects.get(id=self.session_id)
            return s.active_user_id or s.owner_id
        except CollabSession.DoesNotExist:
            return None

    @database_sync_to_async
    def _transfer_control(self, user_id: int):
        from apps.collab.models import CollabSession
        CollabSession.objects.filter(id=self.session_id).update(active_user_id=user_id)
