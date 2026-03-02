"""
Throttle классы для эндпоинтов задач.
"""
from rest_framework.throttling import UserRateThrottle


class TaskStartThrottle(UserRateThrottle):
    """
    Лимит на старт задачи — каждый старт создаёт Docker контейнер.
    5 стартов в минуту достаточно для нормального использования.
    """
    scope = 'task_start'


class TaskCheckThrottle(UserRateThrottle):
    """
    Лимит на проверку задачи — каждая проверка делает Docker exec.
    20 проверок в минуту — с запасом для активных пользователей.
    """
    scope = 'task_check'
