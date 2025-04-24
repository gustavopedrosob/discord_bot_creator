from PySide6.QtCore import QTranslator

from core.config import instance as config
from core.singleton import SingletonMeta


class Translator(metaclass=SingletonMeta):
    def __init__(self):
        self.__instance = QTranslator()
        self.__instance.load(f"translations/build/{config.get("language")}.qm")

    @classmethod
    def translate(cls, context: str, text: str) -> str:
        translator = Translator()
        return translator.get_instance().translate(context, text)

    def get_instance(self) -> QTranslator:
        return self.__instance
    
FIELDS_TRANSLATIONS = {
    "message": Translator.translate("Field", "Message"),
    "author name": Translator.translate("Field", "Author Name"),
    "channel name": Translator.translate("Field", "Channel Name"),
    "guild name": Translator.translate("Field", "Guild Name"),
    "mentions to bot": Translator.translate("Field", "Mentions to Bot"),
    "mentions": Translator.translate("Field", "Mentions"),
    "bot author": Translator.translate("Field", "Bot Author"),
    "emojis": Translator.translate("Field", "Emojis"),
}

OPERATORS_TRANSLATIONS = {
    "equal to": Translator.translate("Operator", "Equal to"),
    "not equal to": Translator.translate("Operator", "Not equal to"),
    "contains": Translator.translate("Operator", "Contains"),
    "not contains": Translator.translate("Operator", "Not contains"),
    "starts with": Translator.translate("Operator", "Starts with"),
    "ends with": Translator.translate("Operator", "Ends with"),
    "regex": Translator.translate("Operator", "Regex"),
    "is greater than": Translator.translate("Operator", "Is greater than"),
    "is less than": Translator.translate("Operator", "Is less than"),
    "is greater or equal to": Translator.translate("Operator", "Is greater or equal to"),
    "is less or equal to": Translator.translate("Operator", "Is less or equal to"),
}

BOOL_TRANSLATIONS = {
    True: Translator.translate("Boolean", "True"),
    False: Translator.translate("Boolean", "False"),
}