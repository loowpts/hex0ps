FROM devops-platform/nginx:latest

USER root
# Ломаем права доступа к конфигу
RUN chmod 000 /etc/nginx/nginx.conf

USER devops
CMD ["/bin/bash"]
