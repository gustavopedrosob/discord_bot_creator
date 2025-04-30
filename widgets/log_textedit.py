import logging
import typing

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor, QColor, QTextCharFormat, QTextDocument
from PySide6.QtWidgets import QTextEdit, QApplication
from qfluentwidgets import PlainTextEdit

from utils import colors


class QLogTextEdit(PlainTextEdit):
    _CLASS_PROPERTY_KEY = 1001
    _CLASS_MAP = {
        logging.INFO: colors.TEXT,
        logging.WARNING: colors.WARNING,
        logging.DEBUG: colors.SECONDARY,
        logging.ERROR: colors.DANGER,
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText(self.tr("No logs at moment"))
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.installEventFilter(self)
        style_hints = QApplication.styleHints()
        _color_scheme = style_hints.colorScheme()
        style_hints.colorSchemeChanged.connect(self._on_theme_changed)
        self._recolor_by_class(
            colors.DARK_THEME if self._is_dark_mode() else colors.LIGHT_THEME
        )

    @staticmethod
    def _is_dark_mode():
        style_hints = QApplication.styleHints()
        color_scheme = style_hints.colorScheme()
        return color_scheme.value == 2

    def add_log(self, message: str, level: typing.Optional[int] = logging.INFO):
        cursor = self.textCursor()
        cursor.movePosition(
            QTextCursor.MoveOperation.End, QTextCursor.MoveMode.MoveAnchor
        )
        class_ = self._CLASS_MAP.get(level, colors.PRIMARY)
        color_map = colors.DARK_THEME if self._is_dark_mode() else colors.LIGHT_THEME
        color = color_map[class_]
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        fmt.setProperty(self._CLASS_PROPERTY_KEY, class_)
        cursor.insertText(message, fmt)

    def _on_theme_changed(self):
        color_map = colors.DARK_THEME if self._is_dark_mode() else colors.LIGHT_THEME
        self._recolor_by_class(color_map)

    @staticmethod
    def _get_text_fragments(doc: QTextDocument):
        block = doc.firstBlock()
        while block.isValid():
            it = block.begin()
            while not it.atEnd():
                yield it.fragment()
                it += 1
            block = block.next()

    def _recolor_by_class(self, color_map: dict[str, QColor]):
        doc = self.document()
        cursor = QTextCursor(doc)

        for fragment in self._get_text_fragments(doc):
            if fragment.isValid():
                fmt = fragment.charFormat()
                if fmt.hasProperty(self._CLASS_PROPERTY_KEY):
                    color_class = fmt.property(self._CLASS_PROPERTY_KEY)
                    if color_class in color_map:
                        new_fmt = QTextCharFormat(fmt)
                        new_fmt.setForeground(color_map[color_class])
                        cursor.setPosition(fragment.position())
                        cursor.setPosition(
                            fragment.position() + fragment.length(),
                            QTextCursor.MoveMode.KeepAnchor,
                        )
                        cursor.setCharFormat(new_fmt)
