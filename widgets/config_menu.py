from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QWidget

from core.config import Config
from widgets.language_menu import QLanguageMenu
from widgets.log_level_menu import QLogLevelMenu

translate = QCoreApplication.translate


class QConfigMenu(QMenu):
    def __init__(self, text: str, parent: QWidget):
        super().__init__(text, parent)
        self.language = QLanguageMenu(translate("MainWindow", "Language"), parent)
        self.log_level = QLogLevelMenu(translate("MainWindow", "Log level"), parent)
        self.auto_start_bot = QAction(translate("MainWindow", "Auto start bot"), parent)
        self.auto_start_bot.setCheckable(True)
        self.auto_start_bot.setChecked(Config.get("auto_start_bot"))
        self._setup_menus()
        self._setup_binds()

    def _setup_menus(self):
        self.addMenu(self.log_level)
        self.addMenu(self.language)
        self.addAction(self.auto_start_bot)

    def on_auto_start_bot_changed(self):
        Config.set("auto_start_bot", self.auto_start_bot.isChecked())
        Config.save()

    def _setup_binds(self):
        self.auto_start_bot.triggered.connect(self.on_auto_start_bot_changed)
