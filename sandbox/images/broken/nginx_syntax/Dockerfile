FROM devops-platform/nginx:latest

USER root
# Вносим синтаксическую ошибку — лишняя точка с запятой
RUN sed -i 's/worker_processes auto;/worker_processes auto;;/' /etc/nginx/nginx.conf

USER devops
CMD ["/bin/bash"]
