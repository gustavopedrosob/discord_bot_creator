import logging
import typing
from pathlib import Path

import yaml

from core.singleton import SingletonMeta


class Config(metaclass=SingletonMeta):
    _default_content = {
        "token": "",
        "language": "en_us",
        "database": ":memory:",
        "log_level": logging.INFO,
    }
    _file = Path(__file__).parent.parent / "config.yaml"

    def __init__(self):
        if self._file.exists() and self._file.is_file():
            self.content = self._load()
        else:
            self.content = self._default_content.copy()
            self.save()

    @classmethod
    def load(cls):
        cls().content = cls._load()

    @classmethod
    def _load(cls):
        with open(cls._file, "r") as file:
            return yaml.load(file, Loader=yaml.FullLoader)

    @classmethod
    def save(cls):
        with open(cls._file, "w") as file:
            yaml.dump(cls().content, file)

    @classmethod
    def get(cls, variable: str):
        return cls().content[variable]

    @classmethod
    def set(cls, variable: str, value: typing.Union[str, int, bool] = None):
        cls().content[variable] = value
