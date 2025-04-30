from PySide6.QtCore import Qt
from extra_qwidgets.utils import adjust_brightness
from qfluentwidgets import PushButton, setCustomStyleSheet


class ColoredPushButton(PushButton):
    def __init__(self, color: str):
        super().__init__()
        hover_color = adjust_brightness(color, 10)
        pressed_color = adjust_brightness(color, -10)
        disabled_color = adjust_brightness(color, -20)
        light_qss = """
        PushButton {
            background-color: %s;
            color: white;
        }
        PushButton:hover {
            background-color: %s;
            color: white;
        }
        PushButton:pressed {
            background-color: %s;
            color: white;
        }
        PushButton:disabled {
            background-color: %s;
            color: white;
        }
        """ % (
            color,
            hover_color,
            pressed_color,
            disabled_color,
        )
        # Mesmas regras para tema escuro, se desejar
        dark_qss = light_qss

        # Aplica apenas ao my_button
        setCustomStyleSheet(self, light_qss, dark_qss)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
