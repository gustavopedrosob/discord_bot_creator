from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox


class QCustomCheckBox(QCheckBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
