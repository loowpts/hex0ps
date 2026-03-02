FROM devops-platform/nginx:latest

USER root
# Запускаем nginx на порту 8080 внутри контейнера, но маппинг наружу сделан на 80
# Симптом: контейнер стартует но соединение отклоняется
RUN sed -i 's/listen 80 default_server/listen 8080 default_server/' /etc/nginx/sites-available/default && \
    sed -i 's/listen \[::\]:80/listen [::]:8080/' /etc/nginx/sites-available/default

# Добавляем конкурирующий процесс на порту 80 (имитируем занятый порт)
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

USER devops
CMD ["/bin/bash"]
