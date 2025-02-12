from PySide6.QtCore import QSize
from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QDialog,
)
from extra_qwidgets.widgets.emoji_picker.emoji_picker import QEmojiPicker


class QEmojiPickerPopup(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setFixedSize(QSize(500, 500))
        self.__emoji_picker = QEmojiPicker(False, False)
        layout = QVBoxLayout()
        layout.addWidget(self.__emoji_picker)
        self.setLayout(layout)

    def emoji_picker(self):
        return self.__emoji_picker
