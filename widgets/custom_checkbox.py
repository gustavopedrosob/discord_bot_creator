from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox


class QCustomCheckBox(QCheckBox):
    def __init__(self, name: str, text: str):
        super().__init__(text)
        self.setObjectName(name)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
