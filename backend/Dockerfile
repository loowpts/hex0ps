FROM python:3.11-slim-bookworm

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Устанавливаем Python зависимости
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/dev.txt

# Копируем исходный код
COPY . .

# Создаём директории для медиа и статики
RUN mkdir -p media staticfiles

# Entrypoint: migrate + collectstatic + loaddata при каждом старте
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
