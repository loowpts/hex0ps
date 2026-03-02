#!/bin/sh
set -e

wait_for_db() {
  echo "[entrypoint] Waiting for database..."
  until python -c "
import os, psycopg2
try:
    psycopg2.connect(
        host=os.environ.get('DB_HOST','db'),
        port=os.environ.get('DB_PORT',5432),
        dbname=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
    )
except Exception:
    exit(1)
" 2>/dev/null; do
    sleep 2
  done
  echo "[entrypoint] Database is ready."
}

# Проверяем что это основной сервер (daphne), а не celery
if echo "$@" | grep -q "daphne"; then
  wait_for_db

  echo "[entrypoint] Migrations..."
  python manage.py makemigrations --noinput
  python manage.py migrate --noinput

  echo "[entrypoint] Static files..."
  python manage.py collectstatic --noinput

  echo "[entrypoint] Loading fixtures..."
  python manage.py loaddata fixtures/tasks.json 2>/dev/null || true
  python manage.py loaddata fixtures/interview_questions.json 2>/dev/null || true
  python manage.py loaddata fixtures/courses.json 2>/dev/null || true
  python manage.py loaddata fixtures/cheatsheets.json 2>/dev/null || true

  echo "[entrypoint] Default user..."
  python manage.py shell -c "
from apps.users.models import User
if not User.objects.exists():
    User.objects.create_superuser(username='admin', password='admin123')
    print('Created default user: admin / admin123')
else:
    print('Users already exist:', User.objects.count())
"

  echo "[entrypoint] Done."
else
  # celery-worker / celery-beat — только ждём БД
  wait_for_db
fi

exec "$@"
