FROM devops-platform/base:latest

USER root

RUN apt-get update && apt-get install -y systemd && rm -rf /var/lib/apt/lists/*

# Создаём сломанный unit файл — ExecStart указывает на несуществующий бинарник
RUN cat > /etc/systemd/system/myapp.service << 'EOF'
[Unit]
Description=My Application
After=network.target

[Service]
ExecStart=/usr/bin/nonexistent-binary --config /etc/myapp/config.yml
Restart=always
User=devops

[Install]
WantedBy=multi-user.target
EOF

USER devops
CMD ["/bin/bash"]
