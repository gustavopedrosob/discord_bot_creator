from PySide6.QtGui import QActionGroup, QAction
from PySide6.QtWidgets import QMenu, QWidget


class QLanguageMenu(QMenu):
    def __init__(self, text: str, parent: QWidget, language: str):
        super().__init__(text, parent)

        self.action_group = QActionGroup(self)
        self.action_group.setExclusive(True)
        self.english_action = QAction(
            "English", self, checked=language == "en_us", checkable=True
        )
        self.portuguese_action = QAction(
            "Portuguese", self, checked=language == "pt_br", checkable=True
        )
        self.setup_actions()

    def setup_actions(self):
        language_actions = (self.english_action, self.portuguese_action)
        for a in language_actions:
            self.action_group.addAction(a)
        self.addActions(language_actions)
