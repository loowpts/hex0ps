"""
Система достижений DevOps Learning Platform.
Проверяет и выдаёт достижения после выполнения задач.
"""
from django.utils import timezone


# Список всех достижений платформы
ACHIEVEMENTS = [
    {
        'key': 'first_task',
        'title_ru': 'Первый шаг',
        'description_ru': 'Выполни первую задачу',
        'icon': '🚀',
        'condition_type': 'completed_tasks_count',
        'condition_value': {'min': 1},
    },
    {
        'key': 'streak_7',
        'title_ru': 'Неделя без пропусков',
        'description_ru': '7 дней активности подряд',
        'icon': '🔥',
        'condition_type': 'streak',
        'condition_value': {'min': 7},
    },
    {
        'key': 'streak_30',
        'title_ru': 'Месяц упорства',
        'description_ru': '30 дней активности подряд',
        'icon': '💪',
        'condition_type': 'streak',
        'condition_value': {'min': 30},
    },
    {
        'key': 'no_hints_10',
        'title_ru': 'Самостоятельность',
        'description_ru': 'Реши 10 задач без подсказок',
        'icon': '⚡',
        'condition_type': 'no_hints_tasks',
        'condition_value': {'min': 10},
    },
    {
        'key': 'breakfix_5',
        'title_ru': 'Антикризисный менеджер',
        'description_ru': 'Реши 5 задач в режиме Break & Fix',
        'icon': '🔧',
        'condition_type': 'breakfix_tasks',
        'condition_value': {'min': 5},
    },
    {
        'key': 'docker_master',
        'title_ru': 'Docker мастер',
        'description_ru': 'Выполни все задачи категории Docker',
        'icon': '🐳',
        'condition_type': 'category_complete',
        'condition_value': {'category': 'docker'},
    },
    {
        'key': 'linux_master',
        'title_ru': 'Linux мастер',
        'description_ru': 'Выполни все задачи категории Linux',
        'icon': '🐧',
        'condition_type': 'category_complete',
        'condition_value': {'category': 'linux'},
    },
    {
        'key': 'xp_1000',
        'title_ru': 'Тысяча очков',
        'description_ru': 'Набери 1000 XP',
        'icon': '⭐',
        'condition_type': 'xp',
        'condition_value': {'min': 1000},
    },
    {
        'key': 'tasks_50',
        'title_ru': 'Полсотни задач',
        'description_ru': 'Выполни 50 задач',
        'icon': '🏆',
        'condition_type': 'completed_tasks_count',
        'condition_value': {'min': 50},
    },
]


def check_and_award_achievements(user) -> list:
    """
    Проверяет все достижения и выдаёт новые пользователю.
    Вызывается после каждого выполнения задачи.
    Возвращает список новых достижений.
    """
    from apps.tasks.models import Task, UserTask
    from apps.users.models import User

    # Достижения, которые уже есть у пользователя
    from django.apps import apps
    UserAchievement = apps.get_model('tasks', 'UserAchievement')
    Achievement = apps.get_model('tasks', 'Achievement')

    existing_keys = set(
        UserAchievement.objects.filter(user=user)
        .values_list('achievement__condition_type', flat=True)
    )

    # Собираем данные для проверки условий
    completed_tasks = UserTask.objects.filter(user=user, status='completed').select_related('task')
    completed_count = completed_tasks.count()
    no_hints_count = sum(1 for t in completed_tasks if t.hints_used == 0)
    breakfix_count = sum(1 for t in completed_tasks if t.task.task_type == 'break_and_fix')

    new_achievements = []

    for ach_data in ACHIEVEMENTS:
        # Пропускаем уже полученные
        if ach_data['key'] in existing_keys:
            continue

        earned = False
        condition_type = ach_data['condition_type']
        condition_value = ach_data['condition_value']

        if condition_type == 'completed_tasks_count':
            earned = completed_count >= condition_value['min']
        elif condition_type == 'streak':
            earned = user.streak >= condition_value['min']
        elif condition_type == 'no_hints_tasks':
            earned = no_hints_count >= condition_value['min']
        elif condition_type == 'breakfix_tasks':
            earned = breakfix_count >= condition_value['min']
        elif condition_type == 'xp':
            earned = user.xp >= condition_value['min']
        elif condition_type == 'category_complete':
            category = condition_value['category']
            total_in_cat = Task.objects.filter(category=category, is_active=True).count()
            completed_in_cat = completed_tasks.filter(task__category=category).count()
            earned = total_in_cat > 0 and completed_in_cat >= total_in_cat

        if earned:
            # Находим или создаём запись достижения в БД
            achievement, _ = Achievement.objects.get_or_create(
                condition_type=ach_data['key'],
                defaults={
                    'title_ru': ach_data['title_ru'],
                    'description_ru': ach_data['description_ru'],
                    'icon': ach_data['icon'],
                    'condition_value': ach_data['condition_value'],
                }
            )

            # Выдаём пользователю
            UserAchievement.objects.get_or_create(
                user=user,
                achievement=achievement,
            )
            new_achievements.append({
                'title_ru': ach_data['title_ru'],
                'description_ru': ach_data['description_ru'],
                'icon': ach_data['icon'],
            })

    return new_achievements


def get_user_achievements_data(user) -> list:
    """
    Возвращает список достижений пользователя для публичного профиля.
    """
    from django.apps import apps
    UserAchievement = apps.get_model('tasks', 'UserAchievement')

    user_achievements = UserAchievement.objects.filter(user=user).select_related('achievement')
    return [
        {
            'icon': ua.achievement.icon,
            'title_ru': ua.achievement.title_ru,
            'earned_at': ua.earned_at.date().isoformat(),
        }
        for ua in user_achievements
    ]
