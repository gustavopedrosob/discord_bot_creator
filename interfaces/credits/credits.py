from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QIcon, QPixmap, Qt
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout


class CreditsWindow:
    def __init__(self):
        self.window = QDialog()
        self.window.setWindowTitle(QCoreApplication.translate("QMainWindow", "Credits"))
        self.window.setFixedSize(400, 200)
        self.window.setWindowIcon(QIcon("source/icons/window-icon.svg"))

        self.layout = QVBoxLayout()

        pixmap = QPixmap("source/icons/icon.svg")
        self.logo = QLabel()
        self.logo.setPixmap(pixmap)

        self.label = QLabel(QCoreApplication.translate("QMainWindow", "Credits text"))

        self.layout.addWidget(self.logo)
        self.layout.addWidget(self.label)

        # centraliza os widgets
        self.layout.setAlignment(self.logo, Qt.AlignmentFlag.AlignCenter)
        self.layout.setAlignment(self.label, Qt.AlignmentFlag.AlignCenter)

        self.window.setLayout(self.layout)
