from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox
from qfluentwidgets import CheckBox


class QCustomCheckBox(CheckBox):
    def __init__(self, name: str, text: str):
        super().__init__()
        self.setText(text)
        self.setObjectName(name)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
