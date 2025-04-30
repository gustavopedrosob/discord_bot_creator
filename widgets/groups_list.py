from PySide6.QtCore import QPoint, Qt, QCoreApplication
from PySide6.QtGui import QAction
from qfluentwidgets import ListWidget, RoundMenu

translate = QCoreApplication.translate


class QGroupsList(ListWidget):
    def __init__(self):
        super().__init__()

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.group_context_menu_event)

        self.config_action = QAction(translate("MainWindow", "Config group"), self)
        self.quit_action = QAction(translate("MainWindow", "Quit group"), self)

    def group_context_menu_event(self, position: QPoint):
        if bool(self.selectedIndexes()):
            context_menu = RoundMenu()
            context_menu.addAction(self.config_action)
            context_menu.addAction(self.quit_action)
            context_menu.exec(self.mapToGlobal(position))
