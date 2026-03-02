"""
Модели для терминальных сессий и записей.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class TerminalSession(models.Model):
    """
    Сессия работы пользователя в Docker-терминале.
    Один контейнер = одна сессия.
    """

    STATUS_PENDING = 'pending'
    STATUS_ACTIVE = 'active'
    STATUS_COMPLETED = 'completed'
    STATUS_EXPIRED = 'expired'
    STATUS_ERROR = 'error'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Ожидает'),
        (STATUS_ACTIVE, 'Активна'),
        (STATUS_COMPLETED, 'Завершена'),
        (STATUS_EXPIRED, 'Истекла'),
        (STATUS_ERROR, 'Ошибка'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='terminal_sessions',
        verbose_name='Пользователь'
    )
    task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.CASCADE,
        related_name='terminal_sessions',
        verbose_name='Задача'
    )
    container_id = models.CharField(max_length=64, blank=True, verbose_name='ID контейнера')
    container_name = models.CharField(max_length=100, blank=True, verbose_name='Имя контейнера')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Статус'
    )
    # Запись сессии в формате asciinema v2: [[time, "o", "data"], ...]
    recording = models.JSONField(default=list, verbose_name='Запись сессии')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    expires_at = models.DateTimeField(verbose_name='Истекает')

    class Meta:
        verbose_name = 'Терминальная сессия'
        verbose_name_plural = 'Терминальные сессии'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f'{self.user.username} — {self.task.title_ru} [{self.get_status_display()}]'

    def is_expired(self) -> bool:
        """Проверяет истекла ли сессия."""
        return timezone.now() > self.expires_at

    def time_remaining_seconds(self) -> int:
        """Сколько секунд осталось до истечения."""
        delta = self.expires_at - timezone.now()
        return max(0, int(delta.total_seconds()))


class SessionRecording(models.Model):
    """
    Публичная запись терминальной сессии для шеринга.
    Формат asciinema v2.
    """

    session = models.OneToOneField(
        TerminalSession,
        on_delete=models.CASCADE,
        related_name='session_recording',
        verbose_name='Сессия'
    )
    share_id = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='ID для шеринга')
    events_json = models.JSONField(verbose_name='События (asciinema формат)')
    cols = models.PositiveIntegerField(default=80, verbose_name='Столбцы терминала')
    rows = models.PositiveIntegerField(default=24, verbose_name='Строки терминала')
    duration_seconds = models.FloatField(default=0, verbose_name='Длительность (сек)')
    is_public = models.BooleanField(default=False, verbose_name='Публичная')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')

    class Meta:
        verbose_name = 'Запись сессии'
        verbose_name_plural = 'Записи сессий'

    def __str__(self):
        return f'Запись {self.share_id} ({self.duration_seconds:.0f}с)'


class PlaygroundSession(models.Model):
    """
    Свободная терминальная сессия без задачи и чекера.
    Пользователь просто практикуется в выбранном окружении.
    Контейнер живёт 30 минут и удаляется автоматически.
    """

    ENV_UBUNTU = 'ubuntu-22'
    ENV_UBUNTU_NGINX = 'ubuntu-22-nginx'
    ENV_ALPINE = 'alpine'

    ENV_CHOICES = [
        (ENV_UBUNTU, 'Ubuntu 22.04'),
        (ENV_UBUNTU_NGINX, 'Ubuntu 22.04 + nginx'),
        (ENV_ALPINE, 'Alpine Linux'),
    ]

    # Маппинг env → docker образ
    ENV_IMAGES = {
        ENV_UBUNTU: 'devops-platform/base:latest',
        ENV_UBUNTU_NGINX: 'devops-platform/nginx:latest',
        ENV_ALPINE: 'devops-platform/base:latest',
    }

    STATUS_ACTIVE = 'active'
    STATUS_EXPIRED = 'expired'
    STATUS_STOPPED = 'stopped'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Активна'),
        (STATUS_EXPIRED, 'Истекла'),
        (STATUS_STOPPED, 'Остановлена'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='playground_sessions',
        verbose_name='Пользователь'
    )
    environment = models.CharField(
        max_length=30,
        choices=ENV_CHOICES,
        default=ENV_UBUNTU,
        verbose_name='Окружение'
    )
    container_id = models.CharField(max_length=64, blank=True, verbose_name='ID контейнера')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    expires_at = models.DateTimeField(verbose_name='Истекает')

    class Meta:
        verbose_name = 'Playground-сессия'
        verbose_name_plural = 'Playground-сессии'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f'{self.user.username} — Playground [{self.environment}] [{self.get_status_display()}]'

    @property
    def docker_image(self):
        return self.ENV_IMAGES.get(self.environment, 'devops-platform/base:latest')

    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    def time_remaining_seconds(self) -> int:
        delta = self.expires_at - timezone.now()
        return max(0, int(delta.total_seconds()))
