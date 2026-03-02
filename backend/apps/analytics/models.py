"""
Модели аналитики: уведомления, changelog.
"""
from django.db import models
from django.conf import settings


class Notification(models.Model):
    """Уведомление для пользователя."""

    TYPE_STREAK_AT_RISK = 'streak_at_risk'
    TYPE_ACHIEVEMENT = 'achievement_earned'
    TYPE_LEVEL_UP = 'level_up'
    TYPE_CERT_ISSUED = 'cert_issued'

    TYPE_CHOICES = [
        (TYPE_STREAK_AT_RISK, 'Риск потери стрика'),
        (TYPE_ACHIEVEMENT, 'Новое достижение'),
        (TYPE_LEVEL_UP, 'Повышение уровня'),
        (TYPE_CERT_ISSUED, 'Выдан сертификат'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Пользователь'
    )
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, verbose_name='Тип')
    message = models.TextField(verbose_name='Сообщение')
    read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'read', 'created_at']),
        ]

    def __str__(self):
        return f'{self.user.username}: {self.get_type_display()}'


class Changelog(models.Model):
    """Записи об обновлениях платформы."""

    version = models.CharField(max_length=20, verbose_name='Версия')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    body_md = models.TextField(verbose_name='Описание (Markdown)')
    published_at = models.DateTimeField(verbose_name='Опубликовано')

    class Meta:
        verbose_name = 'Changelog'
        verbose_name_plural = 'Changelog'
        ordering = ['-published_at']

    def __str__(self):
        return f'v{self.version}: {self.title}'
