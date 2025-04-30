from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QWidget
from qfluentwidgets import MessageBox

translate = QCoreApplication.translate


class QConfirmMessageBox(MessageBox):
    def __init__(self, title: str, text: str, parent: QWidget):
        super().__init__(title, text, parent)
        self.yesButton.setText(translate("MainWindow", "Yes"))
        self.cancelButton.setText(translate("MainWindow", "No"))
