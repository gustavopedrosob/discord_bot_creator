import logging
from datetime import datetime
from PySide6.QtCore import Signal

from core.database import Database
from core.singleton import SingletonMeta


class LogHandler(logging.Handler, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__()
        self.__signal = None

    def emit(self, record: logging.LogRecord):
        date = datetime.fromtimestamp(record.created)
        if self.__signal:
            self.__signal.emit(
                f"{date.strftime("%x %X")} - {record.getMessage()}\n", record.levelno
            )
        Database().new_log(record)

    def set_signal(self, signal: Signal):
        self.__signal = signal


log_handler = LogHandler()
