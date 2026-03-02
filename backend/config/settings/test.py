"""
Настройки для запуска тестов (используют SQLite in-memory).
Не требует запущенных PostgreSQL и Redis.
"""
import os

# Устанавливаем переменные окружения ДО импорта base.py,
# чтобы decouple не упал с UndefinedValueError
os.environ.setdefault('SECRET_KEY', 'test-secret-key-not-for-production-use')
os.environ.setdefault('DATABASE_URL', 'sqlite://:memory:')
os.environ.setdefault('ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver')

from .base import *  # noqa

# --- База данных ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# --- Channels (in-memory, без Redis) ---
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

# --- Celery: выполнять задачи синхронно ---
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# --- Redis (заглушка для тестов) ---
REDIS_URL = 'redis://localhost:6379/0'

# --- Отключаем кэш ---
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# --- Email (в консоль) ---
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# --- Медиафайлы ---
MEDIA_ROOT = '/tmp/devops_test_media'

# --- Отключаем логи AI и внешних сервисов ---
OLLAMA_BASE_URL = 'http://localhost:11434'

# --- Упрощённые пароли в тестах ---
AUTH_PASSWORD_VALIDATORS = []

# --- Throttle: убираем глобальные классы, ставки делаем огромными,
#     чтобы per-view @throttle_classes не падали с KeyError и не давали 429
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'login':      '9999/min',
    'register':   '9999/min',
    'task_start': '9999/min',
    'task_check': '9999/min',
}

# --- Логирование (тихое в тестах) ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {'class': 'logging.NullHandler'},
    },
    'root': {
        'handlers': ['null'],
    },
}
