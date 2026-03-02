"""
Модели системы задач DevOps Learning Platform.
"""
from django.db import models
from django.conf import settings


class Task(models.Model):
    """
    Задача платформы — основная единица обучения.
    Пользователь решает задачи в реальном Docker-терминале.
    """

    # Категории задач
    CATEGORY_LINUX = 'linux'
    CATEGORY_NGINX = 'nginx'
    CATEGORY_SYSTEMD = 'systemd'
    CATEGORY_DOCKER = 'docker'
    CATEGORY_NETWORKS = 'networks'
    CATEGORY_GIT = 'git'
    CATEGORY_CICD = 'cicd'
    CATEGORY_ONBOARDING = 'onboarding'

    CATEGORY_CHOICES = [
        (CATEGORY_LINUX, 'Linux'),
        (CATEGORY_NGINX, 'Nginx'),
        (CATEGORY_SYSTEMD, 'Systemd'),
        (CATEGORY_DOCKER, 'Docker'),
        (CATEGORY_NETWORKS, 'Сети'),
        (CATEGORY_GIT, 'Git'),
        (CATEGORY_CICD, 'CI/CD'),
        (CATEGORY_ONBOARDING, 'Онбординг'),
    ]

    # Уровни сложности
    DIFFICULTY_BEGINNER = 'beginner'
    DIFFICULTY_INTERMEDIATE = 'intermediate'
    DIFFICULTY_ADVANCED = 'advanced'

    DIFFICULTY_CHOICES = [
        (DIFFICULTY_BEGINNER, 'Начинающий'),
        (DIFFICULTY_INTERMEDIATE, 'Средний'),
        (DIFFICULTY_ADVANCED, 'Продвинутый'),
    ]

    # Типы задач
    TYPE_REGULAR = 'regular'
    TYPE_BREAK_AND_FIX = 'break_and_fix'

    TASK_TYPE_CHOICES = [
        (TYPE_REGULAR, 'Обычная'),
        (TYPE_BREAK_AND_FIX, 'Break & Fix'),
    ]

    # Типы чекеров
    CHECKER_PORT = 'port_check'
    CHECKER_SERVICE = 'service_status'
    CHECKER_FILE = 'file_exists'
    CHECKER_COMMAND = 'command_output'

    CHECKER_CHOICES = [
        (CHECKER_PORT, 'Проверка порта'),
        (CHECKER_SERVICE, 'Статус сервиса'),
        (CHECKER_FILE, 'Наличие файла'),
        (CHECKER_COMMAND, 'Вывод команды'),
    ]

    title_ru = models.CharField(max_length=200, verbose_name='Название')
    description_ru = models.TextField(verbose_name='Описание')
    hint_1_ru = models.TextField(verbose_name='Подсказка 1 (бесплатно)')
    hint_2_ru = models.TextField(verbose_name='Подсказка 2 (-25% XP)')
    hint_3_ru = models.TextField(verbose_name='Подсказка 3 (-50% XP)')
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name='Категория'
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        verbose_name='Сложность'
    )
    task_type = models.CharField(
        max_length=20,
        choices=TASK_TYPE_CHOICES,
        default=TYPE_REGULAR,
        verbose_name='Тип задачи'
    )
    xp_reward = models.PositiveIntegerField(default=100, verbose_name='XP награда')
    time_limit = models.PositiveIntegerField(default=30, verbose_name='Лимит времени (мин)')
    docker_image = models.CharField(max_length=100, verbose_name='Docker образ')
    checker_type = models.CharField(
        max_length=30,
        choices=CHECKER_CHOICES,
        verbose_name='Тип чекера'
    )
    # Конфигурация чекера: {"port": 80} или {"service": "nginx"} и т.д.
    checker_config = models.JSONField(default=dict, verbose_name='Конфигурация чекера')
    # Шаги эталонного решения для replay: [{"command": "...", "explanation": "..."}]
    solution_steps = models.JSONField(default=list, verbose_name='Шаги решения')
    # Задачи-предпосылки (нужно выполнить перед этой)
    prerequisites = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='dependent_tasks',
        verbose_name='Предпосылки'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['order', 'id']

    def __str__(self):
        return f'[{self.get_category_display()}] {self.title_ru}'

    @property
    def category_display(self):
        return self.get_category_display()

    @property
    def difficulty_display(self):
        return self.get_difficulty_display()


class UserTask(models.Model):
    """
    Прогресс пользователя по конкретной задаче.
    """

    STATUS_NOT_STARTED = 'not_started'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, 'Не начата'),
        (STATUS_IN_PROGRESS, 'В процессе'),
        (STATUS_COMPLETED, 'Выполнена'),
        (STATUS_FAILED, 'Провалена'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_tasks',
        verbose_name='Пользователь'
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='user_tasks',
        verbose_name='Задача'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NOT_STARTED,
        verbose_name='Статус'
    )
    attempts = models.PositiveIntegerField(default=0, verbose_name='Попытки')
    hints_used = models.PositiveIntegerField(default=0, verbose_name='Подсказок использовано')
    xp_earned = models.PositiveIntegerField(default=0, verbose_name='Заработано XP')
    xp_multiplier = models.FloatField(default=1.0, verbose_name='Множитель XP')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='Начало')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Завершение')
    time_spent = models.PositiveIntegerField(default=0, verbose_name='Потрачено времени (сек)')

    class Meta:
        verbose_name = 'Прогресс по задаче'
        verbose_name_plural = 'Прогресс по задачам'
        unique_together = ['user', 'task']
        indexes = [
            # Горячий путь: фильтрация по пользователю + статусу (5+ мест в коде)
            models.Index(fields=['user', 'status'], name='usertask_user_status_idx'),
            # Используется для статистики завершения (аналитика, прогноз)
            models.Index(fields=['user', 'completed_at'], name='usertask_user_completed_idx'),
        ]

    def __str__(self):
        return f'{self.user.username} — {self.task.title_ru} [{self.get_status_display()}]'

    def calculate_xp_multiplier(self) -> float:
        """
        Рассчитывает множитель XP на основе использованных подсказок.
        Значения множителей — в tasks/constants.py.
        """
        from .constants import XP_HINT_MULTIPLIERS
        hints = min(self.hints_used, 3)
        return XP_HINT_MULTIPLIERS[hints]


class Achievement(models.Model):
    """Достижение платформы."""

    title_ru = models.CharField(max_length=100, verbose_name='Название')
    description_ru = models.TextField(verbose_name='Описание')
    icon = models.CharField(max_length=10, verbose_name='Иконка (эмодзи)')
    condition_type = models.CharField(max_length=30, verbose_name='Тип условия')
    condition_value = models.JSONField(default=dict, verbose_name='Значение условия')

    class Meta:
        verbose_name = 'Достижение'
        verbose_name_plural = 'Достижения'

    def __str__(self):
        return f'{self.icon} {self.title_ru}'


class UserAchievement(models.Model):
    """Достижение, полученное пользователем."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name='Пользователь'
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        verbose_name='Достижение'
    )
    earned_at = models.DateTimeField(auto_now_add=True, verbose_name='Получено')

    class Meta:
        verbose_name = 'Достижение пользователя'
        verbose_name_plural = 'Достижения пользователей'
        unique_together = ['user', 'achievement']

    def __str__(self):
        return f'{self.user.username}: {self.achievement.title_ru}'


class ActivityLog(models.Model):
    """
    Лог активности пользователя.
    Используется для аналитики и heatmap.
    """

    ACTION_TASK_STARTED = 'task_started'
    ACTION_TASK_COMPLETED = 'task_completed'
    ACTION_TASK_FAILED = 'task_failed'
    ACTION_HINT_USED = 'hint_used'
    ACTION_LOGIN = 'login'

    ACTION_CHOICES = [
        (ACTION_TASK_STARTED, 'Начал задачу'),
        (ACTION_TASK_COMPLETED, 'Выполнил задачу'),
        (ACTION_TASK_FAILED, 'Провалил задачу'),
        (ACTION_HINT_USED, 'Использовал подсказку'),
        (ACTION_LOGIN, 'Вошёл в систему'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activity_logs',
        verbose_name='Пользователь'
    )
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        verbose_name='Действие'
    )
    metadata = models.JSONField(default=dict, verbose_name='Метаданные')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    class Meta:
        verbose_name = 'Лог активности'
        verbose_name_plural = 'Логи активности'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action', 'created_at']),
        ]

    def __str__(self):
        return f'{self.user.username}: {self.get_action_display()} в {self.created_at.date()}'


class DailyChallenge(models.Model):
    """Задача дня — каждый день выбирается одна задача для всех пользователей."""

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='daily_challenges',
        verbose_name='Задача'
    )
    date = models.DateField(unique=True, verbose_name='Дата')
    participants_count = models.PositiveIntegerField(default=0, verbose_name='Участников')
    completions_count = models.PositiveIntegerField(default=0, verbose_name='Выполнений')

    class Meta:
        verbose_name = 'Задача дня'
        verbose_name_plural = 'Задачи дня'
        ordering = ['-date']

    def __str__(self):
        return f'Daily {self.date}: {self.task.title_ru}'


class DailyChallengeCompletion(models.Model):
    """Выполнение задачи дня пользователем."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_completions',
        verbose_name='Пользователь'
    )
    challenge = models.ForeignKey(
        DailyChallenge,
        on_delete=models.CASCADE,
        related_name='completions',
        verbose_name='Задача дня'
    )
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name='Завершено')
    time_spent = models.PositiveIntegerField(verbose_name='Потрачено времени (сек)', default=0)
    xp_earned = models.PositiveIntegerField(verbose_name='Заработано XP', default=0)

    class Meta:
        verbose_name = 'Выполнение задачи дня'
        verbose_name_plural = 'Выполнения задачи дня'
        unique_together = ['user', 'challenge']
        ordering = ['time_spent']

    def __str__(self):
        return f'{self.user.username} — {self.challenge.date} ({self.time_spent}s)'
