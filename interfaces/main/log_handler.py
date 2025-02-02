import logging
from datetime import datetime


class LogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.__app = None

    def emit(self, record: logging.LogRecord):
        date = datetime.fromtimestamp(record.created)
        if self.__app:
            self.__app.log(f"{date.strftime("%x %X")} - {record.getMessage()}\n")

    def set_app(self, app):
        self.__app = app


log_handler = LogHandler()
