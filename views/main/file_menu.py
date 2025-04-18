from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QWidget

translate = QCoreApplication.translate


class QFileMenu(QMenu):
    def __init__(self, text: str, parent: QWidget):
        super().__init__(text, parent)
        self.new = QAction(translate("MainWindow", "New file"), self)
        self.load = QAction(translate("MainWindow", "Load"), self)
        self.save = QAction(translate("MainWindow", "Save"), self)
        self.save_as = QAction(translate("MainWindow", "Save as"), self)
        self.exit = QAction(translate("MainWindow", "Exit"), self)

        self.setup_actions()

    def setup_actions(self):
        self.addActions((self.new, self.load, self.save, self.save_as, self.exit))
