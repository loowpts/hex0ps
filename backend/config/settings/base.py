import os
from pathlib import Path
from datetime import timedelta
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY')

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

SITE_URL = config('SITE_URL', default='http://localhost:5173')

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'channels',
]

LOCAL_APPS = [
    'apps.users',
    'apps.tasks',
    'apps.terminal',
    'apps.ai',
    'apps.interview',
    'apps.notes',
    'apps.certs',
    'apps.collab',
    'apps.analytics',
    'apps.courses',
    'apps.cheatsheets',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Кастомная модель пользователя
AUTH_USER_MODEL = 'users.User'

# Пароли
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Локализация
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Статика и медиа
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'task_start': '5/minute',   # создаёт Docker контейнер — дорого
        'task_check': '20/minute',  # Docker exec — умеренно дорого
        'login': '10/minute',       # brute force protection (per IP)
        'register': '5/minute',     # mass account creation protection (per IP)
    },
}

# JWT настройки
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=config('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', default=15, cast=int)
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=config('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=7, cast=int)
    ),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# CORS
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:5173', cast=Csv())
CORS_ALLOW_CREDENTIALS = True

# Redis и Channels
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')

# Django Cache Framework — использует встроенный Redis-backend (Django 4.0+, redis-py уже в deps)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
        'KEY_PREFIX': 'devops',
        'OPTIONS': {
            'socket_connect_timeout': 5,
            'socket_timeout': 5,
        },
    }
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    },
}

# Celery
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/1')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/2')
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

# Celery Beat расписание
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Очистка истёкших терминальных сессий каждую минуту
    'cleanup-expired-sessions': {
        'task': 'apps.terminal.tasks.cleanup_expired_sessions',
        'schedule': crontab(minute='*'),
    },
    # Уведомления о риске потери стрика каждый день в 20:00
    'check-streak-notifications': {
        'task': 'apps.users.tasks.check_streak_notifications',
        'schedule': crontab(hour=20, minute=0),
    },
    # Задача дня — каждый день в 00:00 UTC
    'pick-daily-challenge': {
        'task': 'apps.tasks.pick_daily_challenge',
        'schedule': crontab(hour=0, minute=0),
    },
}

# Ollama AI
OLLAMA_URL = config('OLLAMA_URL', default='http://localhost:11434')
OLLAMA_MODEL = config('OLLAMA_MODEL', default='llama3.2:3b')
# Таймаут HTTP-запроса к Ollama (секунды)
OLLAMA_TIMEOUT = config('OLLAMA_TIMEOUT', default=30, cast=int)
# Жёсткий таймаут для checker (break_and_fix) — не должен блокировать HTTP worker
OLLAMA_CHECKER_TIMEOUT = config('OLLAMA_CHECKER_TIMEOUT', default=15, cast=int)

# Настройки Docker sandbox
DOCKER_SANDBOX_MEMORY_LIMIT = '256m'
DOCKER_SANDBOX_CPU_QUOTA = 50000  # 0.5 CPU
DOCKER_SANDBOX_NETWORK = 'devops_sandbox'
DOCKER_SANDBOX_MAX_PER_HOUR = 10  # Максимум контейнеров в час на пользователя
