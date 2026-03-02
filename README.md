# HexOps — DevOps Learning Platform

Интерактивная платформа для изучения DevOps. Задачи решаются в реальном терминале прямо в браузере — получаешь изолированный Docker-контейнер, выполняешь команды, система проверяет результат и начисляет XP.

---

## Возможности

| | |
|---|---|
| **Реальный терминал** | xterm.js + WebSocket + изолированный Docker-контейнер |
| **Break & Fix** | Задачи со сломанной конфигурацией — найди и исправь |
| **AI-ассистент** | Чат с Ollama (llama3.2:3b) прямо в задаче |
| **Система подсказок** | 3 уровня: бесплатно / −25% XP / −50% XP |
| **Геймификация** | XP, уровни, стрики, достижения, сертификаты PDF |
| **Replay-режим** | Воспроизведение эталонного решения в терминале |
| **Collab-режим** | Совместная работа в одном терминале |
| **Аналитика** | GitHub-style heatmap, навыки по категориям |
| **Command Palette** | Ctrl+K — быстрая навигация |
| **Оффлайн** | Service Worker кэширует задачи и заметки |

---

## Стек

**Backend:** Django 4.2 · DRF · Django Channels · Daphne · Celery · PostgreSQL · Redis · Docker SDK · Ollama · WeasyPrint · SimpleJWT

**Frontend:** React 18 · TypeScript · Vite · Tailwind CSS · TanStack Query · Zustand · xterm.js · Framer Motion · D3.js

---

## Быстрый старт

### Подготовка сервера (Ubuntu 24.04)

Если разворачиваешь на чистом сервере — сначала запусти скрипт, который установит Docker и настроит окружение:

```bash
sudo bash scripts/setup-server.sh
```

После этого переlogинься (или выполни `newgrp docker`) и продолжай.

### Требования
- Docker и Docker Compose
- Доступ к `/var/run/docker.sock` (для запуска контейнеров задач)

### Запуск

```bash
git clone https://github.com/loowpts/hex0ps.git
cd hex0ps
cp .env.example .env
docker compose up --build
```

Открывай браузер:

| | |
|---|---|
| **Платформа** | http://localhost:5173 |
| **API** | http://localhost:8000/api/ |

**Дефолтный аккаунт:** `admin` / `admin123`

При первом запуске автоматически применяются миграции, загружаются фикстуры (задачи, курсы, шпаргалки, вопросы для собесов), создаётся аккаунт администратора.

### Сервисы

| Сервис | Образ | Описание |
|---|---|---|
| `db` | postgres:15-alpine | База данных |
| `redis` | redis:7-alpine | Брокер + кэш |
| `sandbox-builder` | docker:27-cli | Сборка Docker-образов для задач (запускается один раз) |
| `backend` | ./backend/Dockerfile | Django + Daphne (ASGI) |
| `celery` | ./backend/Dockerfile | Воркер задач |
| `celery-beat` | ./backend/Dockerfile | Планировщик задач |
| `frontend` | ./frontend/Dockerfile.dev | React + Vite dev-сервер |
| `ollama` | ollama/ollama:latest | LLM для AI-ассистента |

---

## AI-ассистент

Ollama запускается вместе со всеми сервисами. После старта нужно скачать модель (один раз, ~2 GB):

```bash
docker compose exec ollama ollama pull llama3.2:3b
```

После этого AI-чат в задачах станет доступен.

---

## Конфигурация

Все настройки в `.env`. Скопируй из `.env.example` и измени нужное:

```env
SECRET_KEY=           # обязательно поменяй в продакшне
DEBUG=True
DB_NAME=hexops
DB_USER=postgres
DB_PASSWORD=postgres
```

---

## Структура проекта

```
hexops/
├── backend/                # Django backend
│   ├── apps/
│   │   ├── tasks/          # Задачи, проверщик, XP
│   │   ├── terminal/       # WebSocket терминал, Docker
│   │   ├── users/          # Авторизация, профили, достижения
│   │   ├── analytics/      # Статистика, heatmap
│   │   ├── collab/         # Совместный терминал
│   │   ├── certs/          # Сертификаты PDF
│   │   ├── courses/        # Курсы
│   │   ├── notes/          # Заметки
│   │   ├── interview/      # Вопросы для собеседований
│   │   └── ai/             # Ollama интеграция
│   ├── config/             # Настройки Django
│   └── entrypoint.sh       # Миграции и загрузка данных при старте
├── frontend/               # React + TypeScript
├── sandbox/                # Docker-образы для задач
├── fixtures/               # Начальные данные (курсы, задачи)
├── scripts/                # Вспомогательные скрипты
├── docker-compose.yml
└── .env.example
```
