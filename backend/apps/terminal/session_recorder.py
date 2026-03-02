"""
SessionRecorder — запись терминальной сессии в формате asciinema v2.
"""
import time
import logging

logger = logging.getLogger(__name__)


class SessionRecorder:
    """
    Записывает ввод/вывод терминала в формате asciinema v2.

    Формат:
    Header: {"version": 2, "width": cols, "height": rows, "timestamp": unix_ts}
    Events: [relative_time, "o", "data"]  # output
            [relative_time, "i", "data"]  # input
    """

    def __init__(self, session_id: int, cols: int = 80, rows: int = 24):
        self.session_id = session_id
        self.cols = cols
        self.rows = rows
        self.start_time = time.time()
        self.events: list = []

    def record_output(self, data: str):
        """Записывает вывод терминала."""
        t = round(time.time() - self.start_time, 6)
        self.events.append([t, 'o', data])

    def record_input(self, data: str):
        """Записывает ввод пользователя."""
        t = round(time.time() - self.start_time, 6)
        self.events.append([t, 'i', data])

    def duration(self) -> float:
        """Длительность записи в секундах."""
        if not self.events:
            return 0.0
        return self.events[-1][0]

    def to_asciinema_json(self) -> dict:
        """Возвращает данные в формате asciinema v2."""
        return {
            'version': 2,
            'width': self.cols,
            'height': self.rows,
            'timestamp': int(self.start_time),
            'events': self.events,
        }

    def save(self) -> str | None:
        """
        Сохраняет запись в БД как SessionRecording.
        Возвращает share_id (UUID строка) или None при ошибке.
        """
        try:
            from apps.terminal.models import SessionRecording, TerminalSession

            session = TerminalSession.objects.get(id=self.session_id)
            events_json = self.to_asciinema_json()
            duration = self.duration()

            recording, created = SessionRecording.objects.get_or_create(
                session=session,
                defaults={
                    'events_json': events_json,
                    'cols': self.cols,
                    'rows': self.rows,
                    'duration_seconds': duration,
                    'is_public': False,
                }
            )

            if not created:
                recording.events_json = events_json
                recording.cols = self.cols
                recording.rows = self.rows
                recording.duration_seconds = duration
                recording.save(update_fields=['events_json', 'cols', 'rows', 'duration_seconds'])

            return str(recording.share_id)

        except Exception as e:
            logger.error(f'Ошибка сохранения записи сессии {self.session_id}: {e}')
            return None
