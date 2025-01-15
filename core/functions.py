import ctypes
from datetime import datetime

from PySide6.QtCore import QSettings
from PySide6.QtGui import QPixmap, Qt, QPainter, QColor, QIcon


def random_choose(lista: list):
    from random import choice

    return choice(lista)


def have_in(lista: list, string: str, reverse=False) -> bool:
    if not reverse:
        for x in lista:
            if x in string:
                return True
        return False
    else:
        for x in lista:
            if string in x:
                return True
        return False


def get_time(string: str):
    return datetime.now().strftime(string)


def is_dark_mode() -> bool:
    settings = QSettings(
        "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
        QSettings.Format.NativeFormat,
    )
    return settings.value("AppsUseLightTheme") == 0


def colorize_icon(icon: QIcon, color: str, default_size=(64, 64)) -> QIcon:
    # Get available sizes or use default size if empty
    sizes = icon.availableSizes()

    # Convert QIcon to QPixmap
    if sizes:
        pixmap = icon.pixmap(sizes[0])
    else:
        pixmap = icon.pixmap(*default_size)

    # Create a new QPixmap with the same size and fill it with transparent color
    colored_pixmap = QPixmap(pixmap.size())
    colored_pixmap.fill(Qt.GlobalColor.transparent)

    # Paint the original pixmap onto the new pixmap with the desired color
    painter = QPainter(colored_pixmap)
    painter.drawPixmap(0, 0, pixmap)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(colored_pixmap.rect(), QColor(color))
    painter.end()

    # Convert the colored QPixmap back to QIcon
    return QIcon(colored_pixmap)
