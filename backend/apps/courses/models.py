"""
Модели LMS-слоя: курсы, модули, уроки, квизы, прогресс.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone


class Course(models.Model):
    DIFFICULTY_BEGINNER = 'beginner'
    DIFFICULTY_INTERMEDIATE = 'intermediate'
    DIFFICULTY_ADVANCED = 'advanced'
    DIFFICULTY_CHOICES = [
        (DIFFICULTY_BEGINNER, 'Начинающий'),
        (DIFFICULTY_INTERMEDIATE, 'Средний'),
        (DIFFICULTY_ADVANCED, 'Продвинутый'),
    ]

    slug = models.SlugField(unique=True, max_length=80)
    title_ru = models.CharField(max_length=200)
    description_ru = models.TextField()
    icon = models.CharField(max_length=10, default='📚')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default=DIFFICULTY_BEGINNER)
    category = models.CharField(max_length=30)          # linux / docker / networks / devops
    estimated_hours = models.PositiveIntegerField(default=10)
    xp_reward = models.PositiveIntegerField(default=500)
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='unlocks')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['order']

    def __str__(self):
        return self.title_ru


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title_ru = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Модуль'
        verbose_name_plural = 'Модули'
        ordering = ['order']

    def __str__(self):
        return f'{self.course.title_ru} → {self.title_ru}'


class Lesson(models.Model):
    TYPE_THEORY = 'theory'
    TYPE_QUIZ = 'quiz'
    TYPE_LAB = 'lab'
    TYPE_EXAM = 'exam'
    TYPE_CHOICES = [
        (TYPE_THEORY, 'Теория'),
        (TYPE_QUIZ, 'Тест'),
        (TYPE_LAB, 'Лабораторная'),
        (TYPE_EXAM, 'Экзамен'),
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title_ru = models.CharField(max_length=200)
    lesson_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_THEORY)
    order = models.PositiveIntegerField(default=0)
    xp_reward = models.PositiveIntegerField(default=50)

    # Для type=theory — markdown контент
    content_md = models.TextField(blank=True)

    # Для type=lab — ссылка на существующую Task
    task = models.ForeignKey(
        'tasks.Task',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='lessons',
    )

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['order']

    def __str__(self):
        return f'{self.module.title_ru} → {self.title_ru}'


class Quiz(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz')
    pass_threshold = models.PositiveIntegerField(default=70)  # % для зачёта

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'

    def __str__(self):
        return f'Тест: {self.lesson.title_ru}'


class QuizQuestion(models.Model):
    TYPE_SINGLE = 'single'
    TYPE_MULTI = 'multi'
    TYPE_CHOICES = [
        (TYPE_SINGLE, 'Один вариант'),
        (TYPE_MULTI, 'Несколько вариантов'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text_ru = models.TextField()
    question_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_SINGLE)
    explanation_ru = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text_ru[:80]


class QuizAnswer(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='answers')
    text_ru = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f'{"✓" if self.is_correct else "✗"} {self.text_ru[:60]}'


class QuizAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.PositiveIntegerField()       # % правильных ответов
    passed = models.BooleanField()
    answers_snapshot = models.JSONField()       # {question_id: [answer_id, ...]}
    xp_earned = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} → {self.quiz} ({self.score}%)'


class UserCourseProgress(models.Model):
    STATUS_NOT_STARTED = 'not_started'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, 'Не начат'),
        (STATUS_IN_PROGRESS, 'В процессе'),
        (STATUS_COMPLETED, 'Завершён'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='user_progress')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NOT_STARTED)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    xp_earned = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['user', 'course']
        verbose_name = 'Прогресс по курсу'

    def __str__(self):
        return f'{self.user.username} → {self.course.title_ru} ({self.status})'


class UserLessonProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='user_progress')
    viewed = models.BooleanField(default=False)
    quiz_passed = models.BooleanField(default=False)
    lab_done = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'lesson']
        verbose_name = 'Прогресс по уроку'

    def mark_completed(self):
        if not self.completed:
            self.completed = True
            self.completed_at = timezone.now()
            self.save(update_fields=['completed', 'completed_at'])
            self._check_course_progress()

    def _check_course_progress(self):
        """После завершения урока проверяем — может весь курс пройден."""
        course = self.lesson.module.course
        total = Lesson.objects.filter(module__course=course).count()
        done = UserLessonProgress.objects.filter(
            user=self.user,
            lesson__module__course=course,
            completed=True,
        ).count()
        if total > 0 and done >= total:
            progress, _ = UserCourseProgress.objects.get_or_create(user=self.user, course=course)
            if progress.status != UserCourseProgress.STATUS_COMPLETED:
                progress.status = UserCourseProgress.STATUS_COMPLETED
                progress.completed_at = timezone.now()
                progress.save(update_fields=['status', 'completed_at'])
                self.user.add_xp(course.xp_reward)
