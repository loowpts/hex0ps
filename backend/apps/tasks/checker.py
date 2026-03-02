import logging
import shlex

from docker.errors import DockerException

logger = logging.getLogger(__name__)


def run_checker(task, container_id: str) -> tuple[bool, str]:
    if not container_id:
        return False, 'Контейнер не запущен. Начни задачу заново.'

    try:
        if task.task_type == 'break_and_fix':
            return check_breakfix(task, container_id)
        return run_checker_standard(task, container_id)
    except DockerException as e:
        logger.error(f'Docker ошибка в чекере задачи {task.id}: {e}')
        return False, 'Ошибка Docker при проверке. Попробуй ещё раз.'
    except Exception:
        logger.exception(f'Непредвиденная ошибка чекера для задачи {task.id}')
        return False, 'Ошибка проверки. Попробуй ещё раз.'


def check_port(container_id: str, config: dict) -> tuple[bool, str]:
    """
    Проверяет что порт открыт в контейнере.
    Config: {"port": 80}
    """
    from apps.terminal.docker_manager import DockerManager

    try:
        port = int(config.get('port', 80))
    except (TypeError, ValueError):
        return False, 'Конфигурация чекера неверна: port должен быть числом.'

    if not 1 <= port <= 65535:
        return False, 'Конфигурация чекера неверна: недопустимый номер порта.'

    docker = DockerManager()
    exit_code, output = docker.run_command(
        container_id,
        f'bash -c "nc -z localhost {port} && echo OK || echo FAIL"'
    )

    if exit_code == 0 and 'OK' in output:
        return True, f'Порт {port} открыт!'
    return False, f'Порт {port} не доступен. Убедись что сервис запущен.'


def check_service_status(container_id: str, config: dict) -> tuple[bool, str]:
    """
    Проверяет что systemd-сервис запущен.
    Config: {"service": "nginx"}
    """
    from apps.terminal.docker_manager import DockerManager
    service = config.get('service', '')

    if not service:
        return False, 'Конфигурация чекера неверна.'

    docker = DockerManager()
    # shlex.quote защищает от инъекции в имени сервиса
    exit_code, output = docker.run_command(
        container_id,
        f'systemctl is-active {shlex.quote(service)}'
    )

    if exit_code == 0 and output.strip() == 'active':
        return True, f'Сервис {service} запущен!'
    return False, f'Сервис {service} не запущен. Статус: {output.strip()}'


def check_file_exists(container_id: str, config: dict) -> tuple[bool, str]:
    """
    Проверяет наличие файла и его содержимое.
    Config: {"path": "/etc/nginx/nginx.conf", "expected": "worker_processes"}
    """
    from apps.terminal.docker_manager import DockerManager
    path = config.get('path', '')
    expected = config.get('expected', '')

    if not path:
        return False, 'Конфигурация чекера неверна.'

    docker = DockerManager()

    # shlex.quote защищает path от path traversal и shell injection
    exit_code, _ = docker.run_command(container_id, f'test -f {shlex.quote(path)}')
    if exit_code != 0:
        return False, f'Файл {path} не найден.'

    if expected:
        # -F: фиксированная строка (не regex), оба аргумента экранированы
        exit_code, output = docker.run_command(
            container_id,
            f'grep -qF {shlex.quote(expected)} {shlex.quote(path)} && echo FOUND || echo NOT_FOUND'
        )
        if 'FOUND' not in output:
            return False, 'Файл найден, но не содержит ожидаемого содержимого.'

    return True, f'Файл {path} проверен!'


def check_command_output(container_id: str, config: dict) -> tuple[bool, str]:
    """
    Проверяет вывод команды.
    Config: {"command": "docker ps", "expected": "nginx"}
    """
    from apps.terminal.docker_manager import DockerManager
    command = config.get('command', '')
    expected = config.get('expected', '')

    if not command or not expected:
        return False, 'Конфигурация чекера неверна.'

    docker = DockerManager()
    exit_code, output = docker.run_command(container_id, command)

    if expected in output:
        return True, 'Проверка пройдена!'
    return False, f'Ожидаемый результат не найден. Вывод команды: {output[:200]}'


def check_breakfix(task, container_id: str) -> tuple[bool, str]:
    """
    Специальная проверка для задач типа break_and_fix.
    Сначала выполняет обычную проверку, затем при успехе
    запрашивает у AI объяснение что было сломано.
    """
    # Выполняем стандартную проверку
    success, message = run_checker_standard(task, container_id)

    if not success:
        return False, message

    # При успехе получаем AI-объяснение
    explanation = _get_breakfix_explanation(task)
    if explanation:
        full_message = f'{message}\n\n💡 {explanation}'
        return True, full_message
    return True, message


def run_checker_standard(task, container_id: str) -> tuple[bool, str]:
    """Запускает стандартный чекер без break_and_fix логики."""
    if not container_id:
        return False, 'Контейнер не запущен. Начни задачу заново.'

    checker_type = task.checker_type
    config = task.checker_config

    try:
        if checker_type == 'port_check':
            return check_port(container_id, config)
        elif checker_type == 'service_status':
            return check_service_status(container_id, config)
        elif checker_type == 'file_exists':
            return check_file_exists(container_id, config)
        elif checker_type == 'command_output':
            return check_command_output(container_id, config)
        else:
            return False, f'Неизвестный тип проверки: {checker_type}'
    except DockerException as e:
        logger.error(f'Docker ошибка в чекере задачи {task.id}: {e}')
        return False, 'Ошибка Docker при проверке. Попробуй ещё раз.'
    except Exception:
        logger.exception(f'Непредвиденная ошибка чекера для задачи {task.id}')
        return False, 'Ошибка проверки. Попробуй ещё раз.'


def _get_breakfix_explanation(task) -> str:
    """
    Получает AI-объяснение для break_and_fix задачи.
    Выполняется в отдельном потоке с жёстким таймаутом — не блокирует
    HTTP worker дольше OLLAMA_CHECKER_TIMEOUT секунд.
    """
    from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
    from django.conf import settings

    checker_timeout = getattr(settings, 'OLLAMA_CHECKER_TIMEOUT', 15)

    try:
        from apps.ai.ollama_client import OllamaClient
        client = OllamaClient()

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                client.explain_breakfix,
                task.title_ru,
                task.description_ru or '',
            )
            try:
                return future.result(timeout=checker_timeout)
            except FuturesTimeout:
                logger.warning(
                    f'AI объяснение для задачи {task.id} превысило {checker_timeout}с — пропускаем'
                )
                future.cancel()
                return ''
    except Exception as e:
        logger.warning(f'Не удалось получить AI объяснение для задачи {task.id}: {e}')
        return ''
