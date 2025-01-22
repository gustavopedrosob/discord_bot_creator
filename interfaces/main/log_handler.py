import logging
from datetime import datetime


class LogHandler(logging.Handler):
    def __init__(self, app):
        super().__init__()
        self.__app = app

    def emit(self, record: logging.LogRecord):
        date = datetime.fromtimestamp(record.created)
        self.__app.log(f"{date.strftime("%x %X")} - {record.getMessage()}\n")
