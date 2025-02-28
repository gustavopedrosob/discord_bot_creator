from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QMenuBar, QMenu, QWidget

from interfaces.main.config_menu import QConfigMenu
from interfaces.main.file_menu import QFileMenu
from interfaces.main.help_menu import QHelpMenu

translate = QCoreApplication.translate


class MenuBar(QMenuBar):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.file = QFileMenu(translate("MainWindow", "File"), parent)
        self.config = QConfigMenu(translate("MainWindow", "Config"), parent)
        self.edit = QMenu(translate("MainWindow", "Edit"), parent)
        self.help = QHelpMenu(translate("MainWindow", "Help"), parent)

        self.setup_menus()

    def setup_menus(self):
        for menu in (self.file, self.config, self.edit, self.help):
            self.addMenu(menu)
