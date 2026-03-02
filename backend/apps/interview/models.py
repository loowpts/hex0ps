"""
Модели для системы собеседований.
"""
from django.db import models
from django.conf import settings


class InterviewQuestion(models.Model):
    """Вопрос для собеседования."""

    CATEGORY_CHOICES = [
        ('linux', 'Linux'),
        ('docker', 'Docker'),
        ('nginx', 'Nginx'),
        ('networks', 'Сети'),
        ('systemd', 'Systemd'),
        ('git', 'Git'),
        ('cicd', 'CI/CD'),
    ]

    DIFFICULTY_CHOICES = [
        ('junior', 'Junior'),
        ('middle', 'Middle'),
        ('senior', 'Senior'),
    ]

    question_ru = models.TextField(verbose_name='Вопрос')
    sample_answer_ru = models.TextField(
        verbose_name='Эталонный ответ',
        help_text='НЕ показывается пользователям — только для AI-оценки'
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Категория')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, verbose_name='Сложность')
    tags = models.JSONField(default=list, verbose_name='Теги')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Вопрос для собеседования'
        verbose_name_plural = 'Вопросы для собеседования'
        ordering = ['category', 'difficulty', 'id']

    def __str__(self):
        return f'[{self.category}/{self.difficulty}] {self.question_ru[:50]}...'


class InterviewAttempt(models.Model):
    """Попытка ответа на вопрос собеседования."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interview_attempts',
        verbose_name='Пользователь'
    )
    question = models.ForeignKey(
        InterviewQuestion,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Вопрос'
    )
    user_answer = models.TextField(verbose_name='Ответ пользователя')
    ai_score = models.FloatField(null=True, verbose_name='Оценка AI (1-10)')
    ai_feedback = models.TextField(blank=True, verbose_name='Обратная связь AI')
    ai_strengths = models.JSONField(default=list, verbose_name='Сильные стороны')
    ai_improvements = models.JSONField(default=list, verbose_name='Что улучшить')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')

    class Meta:
        verbose_name = 'Попытка собеседования'
        verbose_name_plural = 'Попытки собеседований'
        ordering = ['-created_at']
        indexes = [
            # Фильтр + сортировка истории попыток пользователя
            models.Index(fields=['user', 'created_at'], name='attempt_user_created_idx'),
        ]

    def __str__(self):
        return f'{self.user.username} — {self.question.question_ru[:40]} (оценка: {self.ai_score})'
