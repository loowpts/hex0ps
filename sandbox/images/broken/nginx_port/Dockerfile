FROM devops-platform/nginx:latest

USER root
# Меняем порт с 80 на 8080 — сервис запускается но на неправильном порту
RUN sed -i 's/listen 80/listen 8080/g' /etc/nginx/sites-available/default

USER devops
CMD ["/bin/bash"]
