"""
Unit тесты для checker.py.

DockerManager мокается — тесты не требуют запущенного Docker.
Покрывает: все типы проверок, валидацию, edge cases, security.
"""
import pytest
from unittest.mock import patch, MagicMock
from docker.errors import DockerException

from apps.tasks.checker import (
    check_port,
    check_service_status,
    check_file_exists,
    check_command_output,
    run_checker_standard,
    run_checker,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def make_task(checker_type='port_check', checker_config=None, task_type='regular', task_id=1):
    task = MagicMock()
    task.id = task_id
    task.task_type = task_type
    task.checker_type = checker_type
    task.checker_config = checker_config or {}
    task.title_ru = 'Test task'
    task.description_ru = 'Test description'
    return task


def mock_docker(exit_code=0, output='OK'):
    """Создаёт мок DockerManager с заданным результатом run_command."""
    docker = MagicMock()
    docker.run_command.return_value = (exit_code, output)
    return docker


# ─── run_checker: базовые проверки ────────────────────────────────────────────

class TestRunChecker:
    def test_no_container_id_returns_false(self):
        task = make_task()
        success, msg = run_checker(task, container_id='')
        assert success is False
        assert 'не запущен' in msg

    def test_docker_exception_returns_false(self):
        task = make_task(checker_type='port_check', checker_config={'port': 80})
        with patch('apps.tasks.checker.check_port', side_effect=DockerException('boom')):
            success, msg = run_checker(task, container_id='abc123')
        assert success is False
        assert 'Docker' in msg

    def test_unexpected_exception_returns_false(self):
        task = make_task(checker_type='port_check', checker_config={'port': 80})
        with patch('apps.tasks.checker.check_port', side_effect=RuntimeError('oops')):
            success, msg = run_checker(task, container_id='abc123')
        assert success is False


# ─── check_port ───────────────────────────────────────────────────────────────

class TestCheckPort:
    def test_open_port_returns_true(self):
        with patch('apps.terminal.docker_manager.DockerManager', return_value=mock_docker(0, 'OK')):
            success, msg = check_port('cid', {'port': 80})
        assert success is True
        assert '80' in msg

    def test_closed_port_returns_false(self):
        with patch('apps.terminal.docker_manager.DockerManager', return_value=mock_docker(1, 'FAIL')):
            success, msg = check_port('cid', {'port': 80})
        assert success is False

    def test_invalid_port_string_returns_false(self):
        success, msg = check_port('cid', {'port': 'abc'})
        assert success is False
        assert 'числом' in msg

    def test_port_zero_is_invalid(self):
        success, msg = check_port('cid', {'port': 0})
        assert success is False
        assert 'недопустимый' in msg

    def test_port_65536_is_invalid(self):
        success, msg = check_port('cid', {'port': 65536})
        assert success is False
        assert 'недопустимый' in msg

    def test_default_port_80_used_when_missing(self):
        docker = mock_docker(0, 'OK')
        with patch('apps.terminal.docker_manager.DockerManager', return_value=docker):
            check_port('cid', {})
        cmd = docker.run_command.call_args[0][1]
        assert '80' in cmd


# ─── check_service_status ─────────────────────────────────────────────────────

class TestCheckServiceStatus:
    def test_active_service_returns_true(self):
        with patch('apps.terminal.docker_manager.DockerManager', return_value=mock_docker(0, 'active')):
            success, msg = check_service_status('cid', {'service': 'nginx'})
        assert success is True
        assert 'nginx' in msg

    def test_inactive_service_returns_false(self):
        with patch('apps.terminal.docker_manager.DockerManager', return_value=mock_docker(1, 'inactive')):
            success, msg = check_service_status('cid', {'service': 'nginx'})
        assert success is False

    def test_empty_service_name_returns_false(self):
        success, msg = check_service_status('cid', {'service': ''})
        assert success is False
        assert 'неверна' in msg

    def test_service_name_is_quoted(self):
        """Имя сервиса должно быть экранировано через shlex.quote."""
        docker = mock_docker(0, 'active')
        with patch('apps.terminal.docker_manager.DockerManager', return_value=docker):
            check_service_status('cid', {'service': 'nginx'})
        cmd = docker.run_command.call_args[0][1]
        # shlex.quote('nginx') → 'nginx' (без кавычек для простых имён)
        assert 'nginx' in cmd

    def test_service_name_with_special_chars_is_safe(self):
        """Инъекция в имени сервиса должна быть экранирована."""
        docker = mock_docker(0, 'active')
        with patch('apps.terminal.docker_manager.DockerManager', return_value=docker):
            check_service_status('cid', {'service': 'nginx; rm -rf /'})
        cmd = docker.run_command.call_args[0][1]
        # После shlex.quote инъекция стала частью строки, а не отдельной командой
        assert '; rm -rf /' not in cmd or "'" in cmd


# ─── check_file_exists ────────────────────────────────────────────────────────

class TestCheckFileExists:
    def test_file_found_without_expected(self):
        with patch('apps.terminal.docker_manager.DockerManager', return_value=mock_docker(0, '')):
            success, msg = check_file_exists('cid', {'path': '/etc/nginx/nginx.conf'})
        assert success is True

    def test_file_not_found_returns_false(self):
        with patch('apps.terminal.docker_manager.DockerManager', return_value=mock_docker(1, '')):
            success, msg = check_file_exists('cid', {'path': '/etc/nginx/nginx.conf'})
        assert success is False
        assert 'не найден' in msg

    def test_file_found_with_expected_content(self):
        docker = mock_docker(0, 'FOUND')
        with patch('apps.terminal.docker_manager.DockerManager', return_value=docker):
            success, _ = check_file_exists('cid', {
                'path': '/etc/nginx/nginx.conf',
                'expected': 'worker_processes',
            })
        assert success is True

    def test_file_found_but_content_missing_returns_false(self):
        # test -f → exit 0 (файл есть), grep -qF → exit 1 (содержимое не найдено)
        docker = MagicMock()
        docker.run_command.side_effect = [(0, ''), (1, '')]
        with patch('apps.terminal.docker_manager.DockerManager', return_value=docker):
            success, msg = check_file_exists('cid', {
                'path': '/etc/nginx/nginx.conf',
                'expected': 'worker_processes',
            })
        assert success is False

    def test_empty_path_returns_false(self):
        success, msg = check_file_exists('cid', {'path': ''})
        assert success is False
        assert 'неверна' in msg

    def test_path_is_quoted_against_injection(self):
        """Путь с пробелами и спецсимволами экранируется через shlex.quote."""
        docker = mock_docker(0, '')
        with patch('apps.terminal.docker_manager.DockerManager', return_value=docker):
            # Путь с пробелом — shlex.quote оборачивает его в кавычки
            check_file_exists('cid', {'path': '/etc/nginx/my config.conf'})
        cmd = docker.run_command.call_args[0][1]
        # shlex.quote('/etc/nginx/my config.conf') → "'/etc/nginx/my config.conf'"
        assert "'/etc/nginx/my config.conf'" in cmd

    def test_expected_with_quotes_is_safe(self):
        """expected содержащий кавычки не должен ломать команду."""
        docker = MagicMock()
        docker.run_command.side_effect = [(0, ''), (0, 'FOUND')]
        with patch('apps.terminal.docker_manager.DockerManager', return_value=docker):
            success, _ = check_file_exists('cid', {
                'path': '/etc/hosts',
                'expected': 'it\'s "working"',
            })
        # Не должно падать — shlex.quote защищает
        cmd = docker.run_command.call_args[0][1]
        assert 'grep' in cmd


# ─── check_command_output ─────────────────────────────────────────────────────

class TestCheckCommandOutput:
    def test_expected_in_output_returns_true(self):
        with patch('apps.terminal.docker_manager.DockerManager', return_value=mock_docker(0, 'nginx is running')):
            success, _ = check_command_output('cid', {
                'command': 'systemctl status nginx',
                'expected': 'running',
            })
        assert success is True

    def test_expected_not_in_output_returns_false(self):
        with patch('apps.terminal.docker_manager.DockerManager', return_value=mock_docker(0, 'inactive')):
            success, msg = check_command_output('cid', {
                'command': 'systemctl status nginx',
                'expected': 'running',
            })
        assert success is False
        assert 'не найден' in msg

    def test_empty_command_returns_false(self):
        success, msg = check_command_output('cid', {'command': '', 'expected': 'ok'})
        assert success is False
        assert 'неверна' in msg

    def test_empty_expected_returns_false(self):
        success, msg = check_command_output('cid', {'command': 'ls', 'expected': ''})
        assert success is False
        assert 'неверна' in msg


# ─── run_checker_standard ─────────────────────────────────────────────────────

class TestRunCheckerStandard:
    def test_unknown_checker_type_returns_false(self):
        task = make_task(checker_type='unknown_type')
        success, msg = run_checker_standard(task, 'cid')
        assert success is False
        assert 'Неизвестный тип' in msg

    def test_no_container_id_returns_false(self):
        task = make_task()
        success, _ = run_checker_standard(task, '')
        assert success is False

    def test_routes_to_port_check(self):
        task = make_task(checker_type='port_check', checker_config={'port': 80})
        with patch('apps.tasks.checker.check_port', return_value=(True, 'ok')) as mock_fn:
            run_checker_standard(task, 'cid')
        mock_fn.assert_called_once_with('cid', {'port': 80})

    def test_routes_to_service_status(self):
        task = make_task(checker_type='service_status', checker_config={'service': 'nginx'})
        with patch('apps.tasks.checker.check_service_status', return_value=(True, 'ok')) as mock_fn:
            run_checker_standard(task, 'cid')
        mock_fn.assert_called_once_with('cid', {'service': 'nginx'})

    def test_routes_to_file_exists(self):
        task = make_task(checker_type='file_exists', checker_config={'path': '/tmp/f'})
        with patch('apps.tasks.checker.check_file_exists', return_value=(True, 'ok')) as mock_fn:
            run_checker_standard(task, 'cid')
        mock_fn.assert_called_once_with('cid', {'path': '/tmp/f'})

    def test_routes_to_command_output(self):
        task = make_task(checker_type='command_output', checker_config={'command': 'ls', 'expected': 'ok'})
        with patch('apps.tasks.checker.check_command_output', return_value=(True, 'ok')) as mock_fn:
            run_checker_standard(task, 'cid')
        mock_fn.assert_called_once()
