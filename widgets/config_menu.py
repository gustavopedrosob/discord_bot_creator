from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QMenu, QWidget

from widgets.language_menu import QLanguageMenu
from widgets.log_level_menu import QLogLevelMenu

translate = QCoreApplication.translate


class QConfigMenu(QMenu):
    def __init__(self, text: str, parent: QWidget):
        super().__init__(text, parent)
        self.language = QLanguageMenu(translate("MainWindow", "Language"), parent)
        self.log_level = QLogLevelMenu(translate("MainWindow", "Log level"), parent)
        self.setup_menus()

    def setup_menus(self):
        self.addMenu(self.log_level)
        self.addMenu(self.language)
