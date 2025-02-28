from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QWidget

translate = QCoreApplication.translate


class QFileMenu(QMenu):
    def __init__(self, text: str, parent: QWidget):
        super().__init__(text, parent)
        self.new_action = QAction(translate("MainWindow", "New file"), self)
        self.load_action = QAction(translate("MainWindow", "Load"), self)
        self.save_action = QAction(translate("MainWindow", "Save"), self)
        self.save_as_action = QAction(translate("MainWindow", "Save as"), self)
        self.exit_action = QAction(translate("MainWindow", "Exit"), self)

        self.setup_actions()

    def setup_actions(self):
        self.addActions(
            (
                self.new_action,
                self.load_action,
                self.save_action,
                self.save_as_action,
                self.exit_action,
            )
        )
