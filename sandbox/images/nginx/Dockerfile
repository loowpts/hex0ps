FROM devops-platform/base:latest

USER root

RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Даём права devops на работу с nginx
RUN chown -R devops:devops /var/log/nginx /var/lib/nginx && \
    chmod 755 /etc/nginx /etc/nginx/sites-enabled /etc/nginx/sites-available && \
    chmod 644 /etc/nginx/nginx.conf

# Стандартная конфигурация
RUN echo '<!DOCTYPE html><html><body><h1>DevOps Platform — Nginx Sandbox</h1></body></html>' \
    > /var/www/html/index.html

USER devops
EXPOSE 80

CMD ["/bin/bash"]
