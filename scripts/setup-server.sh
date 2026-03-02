#!/bin/bash
set -e

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()    { echo -e "${GREEN}[setup]${NC} $1"; }
warn()    { echo -e "${YELLOW}[setup]${NC} $1"; }
error()   { echo -e "${RED}[setup]${NC} $1"; exit 1; }

# Проверяем root
if [ "$EUID" -ne 0 ]; then
  error "Запусти скрипт от root: sudo bash setup-server.sh"
fi

if ! grep -q "24.04" /etc/os-release 2>/dev/null; then
  warn "Скрипт рассчитан на Ubuntu 24.04. Продолжаем на свой страх и риск..."
fi

info "Обновляем пакеты..."
apt-get update -q
apt-get upgrade -y -q

info "Устанавливаем базовые утилиты..."
apt-get install -y -q \
  curl \
  git \
  ca-certificates \
  gnupg \
  lsb-release \
  ufw

# Docker
if command -v docker &>/dev/null; then
  warn "Docker уже установлен: $(docker --version)"
else
  info "Устанавливаем Docker..."
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  chmod a+r /etc/apt/keyrings/docker.gpg

  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
    > /etc/apt/sources.list.d/docker.list

  apt-get update -q
  apt-get install -y -q docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

  systemctl enable --now docker
  info "Docker установлен: $(docker --version)"
fi

# Добавляем текущего пользователя в группу docker
REAL_USER="${SUDO_USER:-$USER}"
if [ "$REAL_USER" != "root" ]; then
  if ! groups "$REAL_USER" | grep -q docker; then
    info "Добавляем $REAL_USER в группу docker..."
    usermod -aG docker "$REAL_USER"
    warn "Для применения изменений группы нужно переlogиниться или выполнить: newgrp docker"
  fi
fi

# Проверяем docker compose v2
if ! docker compose version &>/dev/null; then
  error "docker compose plugin не установлен. Проверь установку Docker."
fi
info "Docker Compose: $(docker compose version)"

# Firewall
info "Настраиваем UFW..."
ufw --force enable
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5173/tcp
ufw allow 8000/tcp
ufw status

info "Готово! Сервер подготовлен."
echo ""
echo "Дальше:"
echo "  git clone https://github.com/loowpts/hex0ps.git"
echo "  cd hex0ps"
echo "  cp .env.example .env && nano .env"
echo "  docker compose up --build -d"
