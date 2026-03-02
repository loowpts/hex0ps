"""
View для дорожной карты обучения.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Task, UserTask


# Структура дорожной карты — зависимости между категориями
ROADMAP_EDGES = [
    {'from': 'linux', 'to': 'systemd'},
    {'from': 'linux', 'to': 'networks'},
    {'from': 'linux', 'to': 'git'},
    {'from': 'systemd', 'to': 'nginx'},
    {'from': 'nginx', 'to': 'docker'},
    {'from': 'docker', 'to': 'cicd'},
    {'from': 'networks', 'to': 'docker'},
]

# Позиции узлов на графе
CATEGORY_POSITIONS = {
    'linux':    {'x': 400, 'y': 50},
    'systemd':  {'x': 200, 'y': 200},
    'networks': {'x': 600, 'y': 200},
    'git':      {'x': 800, 'y': 200},
    'nginx':    {'x': 200, 'y': 350},
    'docker':   {'x': 500, 'y': 350},
    'cicd':     {'x': 500, 'y': 500},
    'onboarding': {'x': 400, 'y': -100},
}

CATEGORY_ICONS = {
    'linux': '🐧',
    'systemd': '⚙️',
    'nginx': '🌐',
    'docker': '🐳',
    'networks': '📡',
    'git': '🌿',
    'cicd': '🔄',
    'onboarding': '👋',
}

CATEGORY_NAMES = {
    'linux': 'Linux Основы',
    'systemd': 'Systemd',
    'nginx': 'Nginx',
    'docker': 'Docker',
    'networks': 'Сети',
    'git': 'Git',
    'cicd': 'CI/CD',
    'onboarding': 'Начало',
}


@api_view(['GET'])
@permission_classes([AllowAny])
def roadmap_view(request):
    """
    Возвращает структуру дорожной карты с прогрессом пользователя.
    Статус узла: locked / available / in_progress / completed
    """
    # Статистика по категориям
    categories = Task.objects.filter(is_active=True).values('category').distinct()
    category_list = [c['category'] for c in categories]

    # Прогресс пользователя
    user_progress = {}
    if request.user.is_authenticated:
        completed_tasks = UserTask.objects.filter(
            user=request.user,
            status='completed'
        ).select_related('task')

        for cat in category_list:
            completed = sum(1 for ut in completed_tasks if ut.task.category == cat)
            user_progress[cat] = completed

    # Строим узлы
    nodes = []
    for cat in category_list:
        total = Task.objects.filter(category=cat, is_active=True).count()
        completed = user_progress.get(cat, 0)

        # Определяем статус
        if completed >= total and total > 0:
            node_status = 'completed'
        elif completed > 0:
            node_status = 'in_progress'
        else:
            # Проверяем заблокированность (< 50% предыдущей категории)
            node_status = _get_node_status(cat, user_progress)

        nodes.append({
            'id': cat,
            'title_ru': CATEGORY_NAMES.get(cat, cat),
            'icon': CATEGORY_ICONS.get(cat, '📦'),
            'completed': completed,
            'total': total,
            'status': node_status,
            'position': CATEGORY_POSITIONS.get(cat, {'x': 0, 'y': 0}),
        })

    return Response({
        'nodes': nodes,
        'edges': ROADMAP_EDGES,
    })


def _get_node_status(category: str, user_progress: dict) -> str:
    """
    Определяет доступность категории на основе прогресса в предыдущих.
    Категория доступна если выполнено >= 50% предыдущей.
    """
    # Находим предыдущие категории (откуда идут стрелки)
    parents = [e['from'] for e in ROADMAP_EDGES if e['to'] == category]

    if not parents:
        # Нет предпосылок — доступно
        return 'available'

    for parent in parents:
        parent_total = Task.objects.filter(category=parent, is_active=True).count()
        parent_completed = user_progress.get(parent, 0)

        if parent_total > 0:
            pct = parent_completed / parent_total
            if pct >= 0.5:
                return 'available'

    return 'locked'
