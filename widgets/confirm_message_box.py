from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QMessageBox, QWidget

translate = QCoreApplication.translate


class QConfirmMessageBox(QMessageBox):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        yes_button = self.button(QMessageBox.StandardButton.Yes)
        yes_button.setText(translate("MainWindow", "Yes"))
        no_button = self.button(QMessageBox.StandardButton.No)
        no_button.setText(translate("MainWindow", "No"))
        self.setDefaultButton(QMessageBox.StandardButton.No)
