import logging
import docker
from docker.errors import NotFound, APIError
from django.conf import settings

logger = logging.getLogger(__name__)


class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.network_name = settings.DOCKER_SANDBOX_NETWORK
        self._ensure_network()

    def _ensure_network(self) -> None:
        try:
            self.client.networks.get(self.network_name)
            logger.debug(f'Сеть {self.network_name} уже существует')
        except NotFound:
            self.client.networks.create(
                self.network_name,
                driver='bridge',
                internal=True,  # Без интернета
                options={
                    'com.docker.network.bridge.enable_ip_masquerade': 'false',
                }
            )
            logger.info(f'Создана изолированная сеть {self.network_name}')
        except Exception as e:
            logger.error(f'Ошибка создания сети: {e}')

    def create_container(self, session) -> str:
        container_name = f'devops_task_{session.id}_{session.user_id}'

        try:
            container = self.client.containers.run(
                image=session.task.docker_image,
                name=container_name,
                mem_limit=settings.DOCKER_SANDBOX_MEMORY_LIMIT,
                cpu_quota=settings.DOCKER_SANDBOX_CPU_QUOTA,
                network=self.network_name,
                user='devops',
                detach=True,
                tty=True,
                stdin_open=True,
                remove=False,
                privileged=False,
                cap_drop=['ALL'],
                security_opt=['no-new-privileges:true'],
                environment={
                    'TERM': 'xterm-256color',
                    'LANG': 'en_US.UTF-8',
                    'HOME': '/home/devops',
                },
                tmpfs={'/tmp': 'size=64m'},
                working_dir='/home/devops',
            )

            logger.info(
                f'Создан контейнер {container.short_id} '
                f'для пользователя {session.user_id}, задача {session.task_id}'
            )
            return container.id

        except APIError as e:
            logger.error(f'Ошибка создания контейнера: {e}')
            raise RuntimeError(f'Не удалось создать контейнер: {e}')

    def get_exec_socket(self, container_id: str):
        """
        Открывает интерактивный exec-сокет (bash) в контейнере.
        Используется WebSocket consumer'ом для stdin/stdout.

        Возвращает tuple (exec_id, socket).
        """
        try:
            container = self.client.containers.get(container_id)

            # Создаём exec с псевдотерминалом
            exec_id = self.client.api.exec_create(
                container.id,
                cmd='/bin/bash',
                stdin=True,
                stdout=True,
                stderr=True,
                tty=True,
                environment={
                    'TERM': 'xterm-256color',
                    'LANG': 'en_US.UTF-8',
                }
            )

            # Открываем socket
            sock = self.client.api.exec_start(
                exec_id['Id'],
                detach=False,
                tty=True,
                socket=True,
            )

            return exec_id['Id'], sock

        except NotFound:
            logger.error(f'Контейнер {container_id[:12]} не найден')
            raise RuntimeError('Контейнер не найден')
        except APIError as e:
            logger.error(f'Ошибка открытия exec: {e}')
            raise RuntimeError(f'Ошибка подключения к контейнеру: {e}')

    def resize_terminal(self, exec_id: str, rows: int, cols: int) -> None:
        """
        Изменяет размер псевдотерминала.
        Вызывается при изменении размера окна браузера.
        """
        try:
            self.client.api.exec_resize(exec_id, height=rows, width=cols)
        except Exception as e:
            logger.warning(f'Ошибка resize терминала: {e}')

    def remove_container(self, container_id: str) -> None:
        """
        Останавливает и удаляет контейнер.
        Безопасно обрабатывает случай когда контейнер уже удалён.
        """
        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=5)
            container.remove(force=True)
            logger.info(f'Удалён контейнер {container_id[:12]}')
        except NotFound:
            logger.debug(f'Контейнер {container_id[:12]} уже не существует')
        except APIError as e:
            logger.error(f'Ошибка удаления контейнера {container_id[:12]}: {e}')

    def container_exists(self, container_id: str) -> bool:
        """Проверяет существование контейнера."""
        try:
            container = self.client.containers.get(container_id)
            return container.status in ('running', 'created', 'paused')
        except NotFound:
            return False
        except Exception:
            return False

    def run_command(self, container_id: str, command: str) -> tuple[int, str]:
        """
        Запускает команду в контейнере неинтерактивно.
        Используется checker'ом для проверки выполнения задачи.

        Возвращает (exit_code, output).
        """
        try:
            container = self.client.containers.get(container_id)
            result = container.exec_run(
                cmd=['bash', '-c', command],
                user='devops',
                stdout=True,
                stderr=True,
                tty=False,
            )
            output = result.output.decode('utf-8', errors='replace').strip()
            return result.exit_code, output
        except NotFound:
            return -1, 'Контейнер не найден'
        except APIError as e:
            logger.error(f'Ошибка выполнения команды в контейнере: {e}')
            return -1, str(e)
