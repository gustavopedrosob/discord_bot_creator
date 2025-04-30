from PySide6.QtCore import QCoreApplication, QPoint
from PySide6.QtGui import QAction, Qt
from PySide6.QtWidgets import QListWidget, QMenu
from qfluentwidgets import ListWidget, RoundMenu

translate = QCoreApplication.translate


class QMessagesList(ListWidget):
    def __init__(self):
        super().__init__()

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.message_context_menu_event)

        self.new_action = QAction(translate("MainWindow", "New message"), self)
        self.new_action.setShortcut("Ctrl+N")
        self.edit_action = QAction(translate("MainWindow", "Edit message"), self)
        self.edit_action.setShortcut("Ctrl+E")
        self.remove_action = QAction(translate("MainWindow", "Remove message"), self)
        self.remove_action.setShortcut("Delete")
        self.remove_all_action = QAction(
            translate("MainWindow", "Remove all messages"), self
        )
        self.remove_all_action.setShortcut("Ctrl+Delete")

    def message_context_menu_event(self, position: QPoint):
        context_menu = RoundMenu()
        context_menu.addAction(self.new_action)
        if bool(self.selectedIndexes()):
            context_menu.addAction(self.edit_action)
            context_menu.addAction(self.remove_action)
        context_menu.addAction(self.remove_all_action)
        context_menu.exec(self.mapToGlobal(position))
