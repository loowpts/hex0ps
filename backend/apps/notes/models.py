"""
Модель заметок — Markdown редактор на странице задачи.
"""
from django.db import models
from django.conf import settings


class Note(models.Model):
    """
    Заметка пользователя — Markdown текст.
    Может быть привязана к задаче или общей (task=None).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name='Пользователь'
    )
    task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notes',
        verbose_name='Задача'
    )
    content = models.TextField(verbose_name='Содержимое (Markdown)')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Заметка'
        verbose_name_plural = 'Заметки'
        unique_together = ['user', 'task']
        ordering = ['-updated_at']
        indexes = [
            # Фильтр по пользователю + сортировка по времени изменения
            models.Index(fields=['user', 'updated_at'], name='note_user_updated_idx'),
        ]

    def __str__(self):
        task_name = self.task.title_ru if self.task else 'Общая заметка'
        return f'{self.user.username}: {task_name}'
