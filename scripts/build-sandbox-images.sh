#!/bin/bash
# Сборка Docker-образов для sandbox задач.
# Порядок важен — производные образы зависят от базового.
set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

info() { echo -e "${GREEN}[sandbox]${NC} $1"; }
err()  { echo -e "${RED}[sandbox]${NC} $1"; exit 1; }

SANDBOX_DIR="$(cd "$(dirname "$0")/../sandbox/images" && pwd)"

build() {
    local name="$1"
    local path="$2"
    info "Собираем $name ..."
    docker build -t "$name" "$path" || err "Ошибка сборки $name"
    info "OK: $name"
}

# 1. Базовый образ
build "devops-platform/base:latest" "$SANDBOX_DIR/base"

# 2. Образы на базе base
build "devops-platform/nginx:latest"  "$SANDBOX_DIR/nginx"

# 3. Сломанные образы (зависят от nginx)
build "devops-platform/broken/nginx_syntax:latest"      "$SANDBOX_DIR/broken/nginx_syntax"
build "devops-platform/broken/nginx_port:latest"        "$SANDBOX_DIR/broken/nginx_port"
build "devops-platform/broken/nginx_permissions:latest" "$SANDBOX_DIR/broken/nginx_permissions"
build "devops-platform/broken/systemd_path:latest"      "$SANDBOX_DIR/broken/systemd_path"
build "devops-platform/broken/docker_port:latest"       "$SANDBOX_DIR/broken/docker_port"

info "Все образы собраны:"
docker images | grep devops-platform
