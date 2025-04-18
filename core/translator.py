from PySide6.QtCore import QTranslator

from core.config import instance as config


class Translator:
    __instance = None

    def __init__(self):
        cls = self.__class__
        if cls.__instance is None:
            cls.__instance = QTranslator()
            cls.__instance.load(f"translations/build/{config.get("language")}.qm")

    @classmethod
    def translate(cls, context: str, text: str) -> str:
        return cls.__instance.translate(context, text)

    @classmethod
    def get_instance(cls) -> QTranslator:
        return cls.__instance

Translator()
