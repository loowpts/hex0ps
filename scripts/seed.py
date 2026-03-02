#!/usr/bin/env python
"""
Скрипт заполнения базы данных тестовыми данными.
Создаёт тестового пользователя, загружает задачи, генерирует активность.
"""
import os
import sys
import random
import django
from datetime import timedelta

# Добавляем backend в Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.utils import timezone
from django.core.management import call_command

from apps.users.models import User
from apps.tasks.models import Task, UserTask, ActivityLog, Achievement, UserAchievement


def create_test_user():
    """Создаёт тестового пользователя."""
    user, created = User.objects.get_or_create(
        email='test@devops.ru',
        defaults={
            'username': 'bbxs',
            'xp': 1450,
            'level': 'junior',
            'streak': 5,
            'max_streak': 12,
            'is_public': True,
            'onboarding_done': True,
            'bio': 'DevOps энтузиаст. Учусь на практике.',
            'last_active': timezone.now().date(),
        }
    )
    if created:
        user.set_password('devops123')
        user.save()
        print(f'✅ Создан пользователь: {user.email}')
    else:
        print(f'ℹ️  Пользователь {user.email} уже существует')
    return user


def load_tasks():
    """Загружает задачи из fixtures."""
    try:
        call_command('loaddata', 'fixtures/tasks.json', verbosity=0)
        count = Task.objects.count()
        print(f'✅ Загружено задач: {count}')
    except Exception as e:
        print(f'⚠️  Ошибка загрузки задач: {e}')


def create_user_tasks(user, count=20):
    """Создаёт записи о выполненных задачах для пользователя."""
    tasks = list(Task.objects.filter(is_active=True))
    if not tasks:
        print('⚠️  Задачи не найдены, пропускаем')
        return

    # Выбираем случайные задачи (не больше чем есть)
    selected = random.sample(tasks, min(count, len(tasks)))
    created_count = 0

    for task in selected:
        hints_used = random.choice([0, 0, 0, 1, 2])  # Чаще без подсказок
        multiplier = {0: 1.0, 1: 1.0, 2: 0.75, 3: 0.50}.get(hints_used, 1.0)

        # Бонус за стрик и без подсказок
        if hints_used == 0:
            multiplier *= 1.10
        if user.streak >= 7:
            multiplier *= 1.15

        xp_earned = int(task.xp_reward * multiplier)
        started_at = timezone.now() - timedelta(days=random.randint(1, 90))
        time_spent = random.randint(300, 2700)  # 5-45 минут

        user_task, created = UserTask.objects.get_or_create(
            user=user,
            task=task,
            defaults={
                'status': 'completed',
                'attempts': random.randint(1, 3),
                'hints_used': hints_used,
                'xp_earned': xp_earned,
                'xp_multiplier': multiplier,
                'started_at': started_at,
                'completed_at': started_at + timedelta(seconds=time_spent),
                'time_spent': time_spent,
            }
        )
        if created:
            created_count += 1

    print(f'✅ Создано {created_count} записей прогресса')


def generate_activity_log(user, days=90):
    """Генерирует историю активности за последние N дней."""
    tasks = list(Task.objects.filter(is_active=True))
    if not tasks:
        return

    created_count = 0
    for day_offset in range(days):
        # Не каждый день активен (реалистично)
        if random.random() > 0.6:
            continue

        day = timezone.now() - timedelta(days=day_offset)
        tasks_that_day = random.randint(1, 4)

        for _ in range(tasks_that_day):
            task = random.choice(tasks)
            ActivityLog.objects.create(
                user=user,
                action=ActivityLog.ACTION_TASK_COMPLETED,
                metadata={
                    'task_id': task.id,
                    'task_title': task.title_ru,
                    'category': task.category,
                    'xp_earned': random.randint(50, 300),
                    'time_spent': random.randint(300, 1800),
                    'hints_used': random.randint(0, 2),
                },
                created_at=day - timedelta(hours=random.randint(0, 8)),
            )
            created_count += 1

    print(f'✅ Создано {created_count} записей активности за {days} дней')


def create_achievements():
    """Создаёт тестовые достижения в БД."""
    from apps.users.achievements import ACHIEVEMENTS

    created_count = 0
    for ach_data in ACHIEVEMENTS:
        achievement, created = Achievement.objects.get_or_create(
            condition_type=ach_data['key'],
            defaults={
                'title_ru': ach_data['title_ru'],
                'description_ru': ach_data['description_ru'],
                'icon': ach_data['icon'],
                'condition_value': ach_data['condition_value'],
            }
        )
        if created:
            created_count += 1

    print(f'✅ Создано {created_count} достижений')

    # Выдаём несколько достижений тестовому пользователю
    user = User.objects.filter(email='test@devops.ru').first()
    if user:
        first_achievements = Achievement.objects.filter(
            condition_type__in=['first_task', 'xp_1000']
        )
        for ach in first_achievements:
            UserAchievement.objects.get_or_create(user=user, achievement=ach)
        print(f'✅ Выдано {first_achievements.count()} достижений тестовому пользователю')


def main():
    print('\n🚀 Начинаем seed базы данных...\n')

    # 1. Загружаем задачи
    load_tasks()

    # 2. Создаём тестового пользователя
    user = create_test_user()

    # 3. Создаём прогресс по задачам
    create_user_tasks(user, count=20)

    # 4. Генерируем историю активности
    generate_activity_log(user, days=90)

    # 5. Создаём достижения
    create_achievements()

    print('\n' + '='*50)
    print('✅ Seed завершён.')
    print(f'   Пользователь: test@devops.ru / devops123')
    print(f'   Задач в БД: {Task.objects.count()}')
    print(f'   Записей активности: {ActivityLog.objects.count()}')
    print('='*50 + '\n')


if __name__ == '__main__':
    main()
