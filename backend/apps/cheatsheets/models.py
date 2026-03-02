"""
Модели для Cheat Sheets — шпаргалок по DevOps командам.
"""
from django.db import models
from django.conf import settings


class CheatSheet(models.Model):
    """
    Шпаргалка по теме — набор команд с описаниями.
    """

    CATEGORY_CHOICES = [
        ('linux', 'Linux'),
        ('nginx', 'Nginx'),
        ('systemd', 'Systemd'),
        ('docker', 'Docker'),
        ('networks', 'Сети'),
        ('git', 'Git'),
        ('cicd', 'CI/CD'),
    ]

    title_ru = models.CharField(max_length=200, verbose_name='Название')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Категория')
    content_md = models.TextField(verbose_name='Содержание (Markdown)')
    tags = models.JSONField(default=list, verbose_name='Теги')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')

    class Meta:
        verbose_name = 'Шпаргалка'
        verbose_name_plural = 'Шпаргалки'
        ordering = ['category', 'order']

    def __str__(self):
        return f'[{self.category}] {self.title_ru}'


class CheatSheetEntry(models.Model):
    """
    Конкретная команда внутри шпаргалки.
    Используется для карточек повторения (Spaced Repetition).
    """

    cheatsheet = models.ForeignKey(
        CheatSheet,
        on_delete=models.CASCADE,
        related_name='entries',
        verbose_name='Шпаргалка'
    )
    command = models.CharField(max_length=300, verbose_name='Команда')
    description_ru = models.CharField(max_length=400, verbose_name='Описание')
    example = models.TextField(blank=True, verbose_name='Пример')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Команда шпаргалки'
        verbose_name_plural = 'Команды шпаргалок'
        ordering = ['order']

    def __str__(self):
        return f'{self.command} — {self.description_ru[:50]}'


class UserCheatSheetBookmark(models.Model):
    """Закладка пользователя на шпаргалку."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cheatsheet_bookmarks',
        verbose_name='Пользователь'
    )
    cheatsheet = models.ForeignKey(
        CheatSheet,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        verbose_name='Шпаргалка'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Добавлено')

    class Meta:
        verbose_name = 'Закладка шпаргалки'
        verbose_name_plural = 'Закладки шпаргалок'
        unique_together = ['user', 'cheatsheet']

    def __str__(self):
        return f'{self.user.username} → {self.cheatsheet.title_ru}'


class UserCheatSheetProgress(models.Model):
    """Прогресс пользователя по конкретной команде ('запомнил' / не запомнил)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cheatsheet_progress',
        verbose_name='Пользователь'
    )
    entry = models.ForeignKey(
        CheatSheetEntry,
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name='Команда'
    )
    learned = models.BooleanField(default=False, verbose_name='Запомнил')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        verbose_name = 'Прогресс по команде'
        verbose_name_plural = 'Прогресс по командам'
        unique_together = ['user', 'entry']

    def __str__(self):
        return f'{self.user.username}: {self.entry.command} — {"✓" if self.learned else "○"}'
