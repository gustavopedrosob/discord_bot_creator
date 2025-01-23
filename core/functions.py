import re
from datetime import datetime
from PySide6.QtCore import QSettings
from PySide6.QtGui import QPixmap, Qt, QPainter, QColor, QIcon
from random import choice


def random_choose(array: list):
    return choice(array)


def has_number(string: str) -> bool:
    return any(char.isnumeric() for char in string)


def has_symbols(string: str) -> bool:
    return bool(re.search(r"[-!$%^&*()_+|~=`{}\[\]:\";'<>?,./\\´§¨#@ªº°]", string))


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


def adjust_brightness(hex_color: str, percentage: float = 10) -> str:
    """
    Ajusta o brilho de uma cor hexadecimal.

    Args:
        hex_color (str): Cor no formato hexadecimal (e.g., '#RRGGBB').
        percentage (float): Porcentagem para ajustar o brilho (positivo para mais brilho, negativo para menos).

    Returns:
        str: Nova cor no formato hexadecimal com o brilho ajustado.
    """
    # Remover o símbolo '#' se presente
    hex_color = hex_color.lstrip("#")

    # Converter o hexadecimal para valores RGB
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

    # Calcular o fator de ajuste
    factor = 1 + (percentage / 100)

    # Aplicar o ajuste e garantir que os valores fiquem no intervalo [0, 255]
    r = min(255, max(0, int(r * factor)))
    g = min(255, max(0, int(g * factor)))
    b = min(255, max(0, int(b * factor)))

    # Converter de volta para hexadecimal
    return f"#{r:02X}{g:02X}{b:02X}"
