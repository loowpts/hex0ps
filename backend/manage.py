#!/usr/bin/env python
"""Утилита командной строки Django для DevOps Learning Platform."""
import os
import sys


def main():
    """Запускает административные задачи."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Не удалось импортировать Django. Убедись что Django установлен "
            "и активирован в виртуальном окружении."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
