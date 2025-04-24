import typing

from PySide6.QtCore import QMimeData, Qt
from PySide6.QtGui import QValidator, QKeyEvent
from extra_qwidgets.widgets import QResponsiveTextEdit


class QMessageTextEdit(QResponsiveTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMaximumHeight(400)
        self.__validator = None

    def validator(self) -> typing.Optional[QValidator]:
        return self.__validator

    def set_validator(self, validator: QValidator):
        self.__validator = validator

    def insertFromMimeData(self, source: QMimeData):
        if source.hasText():
            text = source.text()
            validator = self.validator()
            if validator and validator.validate(text, 0) not in (
                QValidator.State.Intermediate,
                QValidator.State.Acceptable,
            ):
                return
            mime_data = QMimeData()
            mime_data.setText(source.text())
            super().insertFromMimeData(mime_data)

    def keyPressEvent(self, e: QKeyEvent):
        if e.modifiers() == Qt.KeyboardModifier.NoModifier and e.key() not in (
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter,
            Qt.Key.Key_Backspace,
        ):
            text = self.toPlainText() + e.text()
            validator = self.validator()
            if validator and validator.validate(text, 0) not in (
                QValidator.State.Intermediate,
                QValidator.State.Acceptable,
            ):
                return
            super().keyPressEvent(e)
        else:
            super().keyPressEvent(e)
