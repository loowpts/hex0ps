"""
Модели командного режима (Collab) — два пользователя в одном терминале.
"""
import uuid
from django.db import models
from django.conf import settings


class CollabSession(models.Model):
    """
    Сессия совместной работы.
    Owner создаёт сессию, Guest принимает приглашение.
    """

    STATUS_WAITING = 'waiting'
    STATUS_ACTIVE = 'active'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = [
        (STATUS_WAITING, 'Ожидает гостя'),
        (STATUS_ACTIVE, 'Активна'),
        (STATUS_CLOSED, 'Закрыта'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_collabs',
        verbose_name='Владелец'
    )
    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='guest_collabs',
        verbose_name='Гость'
    )
    terminal_session = models.ForeignKey(
        'terminal.TerminalSession',
        on_delete=models.CASCADE,
        verbose_name='Терминальная сессия'
    )
    invite_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        verbose_name='Токен приглашения'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_WAITING,
        verbose_name='Статус'
    )
    active_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='controlling',
        verbose_name='Управляет терминалом'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')

    class Meta:
        verbose_name = 'Командная сессия'
        verbose_name_plural = 'Командные сессии'

    def __str__(self):
        return f'Collab {self.invite_token}: {self.owner.username} + {self.guest.username if self.guest else "?"}'
