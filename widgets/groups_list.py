from PySide6.QtCore import QPoint, Qt, QCoreApplication
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QListWidget, QMenu

translate = QCoreApplication.translate


class QGroupsList(QListWidget):
    def __init__(self):
        super().__init__()

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.group_context_menu_event)

        self.config_action = QAction(translate("MainWindow", "Config group"), self)
        self.quit_action = QAction(translate("MainWindow", "Quit group"), self)

    def group_context_menu_event(self, position: QPoint):
        context_menu = QMenu(self)
        if bool(self.selectedIndexes()):
            context_menu.addActions((self.config_action, self.quit_action))
        context_menu.exec(self.mapToGlobal(position))
