from PySide6.QtCore import QEvent
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLineEdit, QPushButton

from core.functions import is_dark_mode, change_svg_color


class QPassword(QFrame):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)

        self.line_edit = QLineEdit()
        layout.addWidget(self.line_edit)
        self.hide_button = QPushButton()
        layout.addWidget(self.hide_button)

        self.hide_button.clicked.connect(
            lambda: self.set_password_hide(not self.is_password_hide())
        )

        self.set_password_hide(True)

        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.PaletteChange:
            self.__set_icon()
        return super().eventFilter(obj, event)

    def is_password_hide(self) -> bool:
        return self.line_edit.echoMode() == QLineEdit.EchoMode.Password

    def __set_icon(self) -> None:
        hide = self.is_password_hide()
        icon_path = (
            "source/icons/eye-regular.svg"
            if hide
            else "source/icons/eye-slash-regular.svg"
        )
        if is_dark_mode():
            image = change_svg_color(icon_path, "#FFFFFF")
        else:
            image = QIcon(icon_path)
        self.hide_button.setIcon(image)

    def set_password_hide(self, hide: bool) -> None:
        if hide:
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        else:
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        self.__set_icon()
