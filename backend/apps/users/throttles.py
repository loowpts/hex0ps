"""
Throttle классы для аутентификационных эндпоинтов.
"""
from rest_framework.throttling import AnonRateThrottle


class LoginThrottle(AnonRateThrottle):
    """
    Лимит на логин для анонимных пользователей — защита от brute force.
    10 попыток в минуту с одного IP.
    """
    scope = 'login'


class RegisterThrottle(AnonRateThrottle):
    """
    Лимит на регистрацию — защита от массового создания аккаунтов.
    5 регистраций в минуту с одного IP.
    """
    scope = 'register'
