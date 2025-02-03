from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton


class QCustomButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
