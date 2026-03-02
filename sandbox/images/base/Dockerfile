FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8
ENV TERM=xterm-256color

RUN apt-get update && apt-get install -y \
    bash curl wget vim nano \
    net-tools iproute2 iputils-ping \
    procps htop lsof \
    tar gzip zip unzip \
    grep sed gawk findutils \
    git \
    netcat-openbsd \
    tree \
    less \
    man-db \
    locales \
    && locale-gen en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

# Создаём непривилегированного пользователя devops
RUN useradd -m -s /bin/bash devops && \
    echo "devops ALL=(ALL) NOPASSWD: /usr/bin/apt-get, /usr/bin/systemctl" >> /etc/sudoers

USER devops
WORKDIR /home/devops

# Базовые алиасы для удобства
RUN echo 'alias ll="ls -la"' >> ~/.bashrc && \
    echo 'alias la="ls -A"' >> ~/.bashrc && \
    echo 'PS1="\[\033[01;32m\]devops@sandbox\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "' >> ~/.bashrc

CMD ["/bin/bash"]
