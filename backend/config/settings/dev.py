from .base import *  # noqa
from decouple import config

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='devops_platform'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='db'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

if DEBUG:
    import logging
    logging.basicConfig(level=logging.INFO)

CORS_ALLOW_ALL_ORIGINS = True

INSTALLED_APPS += ['django.contrib.admindocs']  # noqa: F405

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
