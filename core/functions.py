from datetime import datetime

from PySide6.QtCore import QSettings
from PySide6.QtGui import QPixmap, Qt, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer


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


def change_svg_color(svg_path: str, color: str) -> QPixmap:
    renderer = QSvgRenderer(svg_path)
    image = QPixmap(renderer.defaultSize())
    image.fill(Qt.GlobalColor.transparent)

    painter = QPainter(image)
    renderer.render(painter)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(image.rect(), QColor(color))
    painter.end()

    return image
