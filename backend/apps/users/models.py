from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    # Уровни пользователя
    LEVEL_BEGINNER = 'beginner'
    LEVEL_JUNIOR = 'junior'
    LEVEL_MIDDLE = 'middle'
    LEVEL_SENIOR = 'senior'
    LEVEL_PRO = 'pro'

    LEVEL_CHOICES = [
        (LEVEL_BEGINNER, 'Новичок'),
        (LEVEL_JUNIOR, 'Junior'),
        (LEVEL_MIDDLE, 'Middle'),
        (LEVEL_SENIOR, 'Senior'),
        (LEVEL_PRO, 'DevOps Pro'),
    ]

    LEVEL_THRESHOLDS = {
        LEVEL_BEGINNER: 0,
        LEVEL_JUNIOR: 500,
        LEVEL_MIDDLE: 2000,
        LEVEL_SENIOR: 5000,
        LEVEL_PRO: 10000,
    }

    email = models.EmailField(blank=True, default='', verbose_name='Email')
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default=LEVEL_BEGINNER,
        verbose_name='Уровень'
    )
    xp = models.PositiveIntegerField(default=0, verbose_name='Опыт')
    streak = models.PositiveIntegerField(default=0, verbose_name='Стрик')
    max_streak = models.PositiveIntegerField(default=0, verbose_name='Максимальный стрик')
    is_public = models.BooleanField(default=True, verbose_name='Публичный профиль')
    onboarding_done = models.BooleanField(default=False, verbose_name='Онбординг завершён')
    last_active = models.DateField(null=True, blank=True, verbose_name='Последняя активность')
    avatar_url = models.URLField(blank=True, verbose_name='URL аватара')
    bio = models.TextField(blank=True, verbose_name='О себе')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def add_xp(self, amount: int) -> None:
        """
        Добавляет XP и автоматически пересчитывает уровень.
        """
        self.xp += amount
        self._recalculate_level()
        self.save(update_fields=['xp', 'level'])

    def _recalculate_level(self) -> None:
        """Пересчитывает уровень на основе текущего XP."""
        thresholds = [
            (self.LEVEL_PRO, 10000),
            (self.LEVEL_SENIOR, 5000),
            (self.LEVEL_MIDDLE, 2000),
            (self.LEVEL_JUNIOR, 500),
            (self.LEVEL_BEGINNER, 0),
        ]
        for level, threshold in thresholds:
            if self.xp >= threshold:
                self.level = level
                break

    def update_streak(self) -> None:
        """
        Обновляет стрик активности:
        - вчера активен → streak+1
        - сегодня уже активен → без изменений
        - давно неактивен → streak=1
        """
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)

        if self.last_active == today:
            # Уже активен сегодня — ничего не меняем
            return
        elif self.last_active == yesterday:
            # Активен вчера — продолжаем стрик
            self.streak += 1
        else:
            # Пропустил день или первый раз — начинаем с 1
            self.streak = 1

        # Обновляем максимальный стрик
        if self.streak > self.max_streak:
            self.max_streak = self.streak

        self.last_active = today
        self.save(update_fields=['streak', 'max_streak', 'last_active'])

    @property
    def xp_to_next_level(self) -> int:
        """Сколько XP осталось до следующего уровня."""
        next_level_thresholds = {
            self.LEVEL_BEGINNER: 500,
            self.LEVEL_JUNIOR: 2000,
            self.LEVEL_MIDDLE: 5000,
            self.LEVEL_SENIOR: 10000,
            self.LEVEL_PRO: None,  # Максимальный уровень
        }
        next_threshold = next_level_thresholds.get(self.level)
        if next_threshold is None:
            return 0
        return max(0, next_threshold - self.xp)

    @property
    def level_progress_pct(self) -> float:
        """Процент прогресса до следующего уровня (0-100)."""
        current_thresholds = {
            self.LEVEL_BEGINNER: (0, 500),
            self.LEVEL_JUNIOR: (500, 2000),
            self.LEVEL_MIDDLE: (2000, 5000),
            self.LEVEL_SENIOR: (5000, 10000),
            self.LEVEL_PRO: (10000, 10000),
        }
        current_min, current_max = current_thresholds.get(self.level, (0, 1))
        if current_min == current_max:
            return 100.0
        progress = (self.xp - current_min) / (current_max - current_min)
        return round(min(100.0, max(0.0, progress * 100)), 1)

    @property
    def level_display(self) -> str:
        """Отображаемое название уровня."""
        return dict(self.LEVEL_CHOICES).get(self.level, self.level)
