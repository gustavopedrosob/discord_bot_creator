from PySide6.QtGui import QActionGroup, QAction
from PySide6.QtWidgets import QMenu, QWidget

from core.config import Config


class QLanguageMenu(QMenu):
    def __init__(self, text: str, parent: QWidget):
        super().__init__(text, parent)

        language = Config.get("language")
        self.action_group = QActionGroup(self)
        self.action_group.setExclusive(True)
        self.english = QAction(
            "English", self, checked=language == "en_us", checkable=True
        )
        self.portuguese = QAction(
            "Portuguese", self, checked=language == "pt_br", checkable=True
        )
        self.setup_actions()

    def setup_actions(self):
        language_actions = (self.english, self.portuguese)
        for a in language_actions:
            self.action_group.addAction(a)
        self.addActions(language_actions)
