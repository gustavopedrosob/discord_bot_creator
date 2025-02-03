from core.functions import adjust_brightness
from interfaces.classes.custom_button import QCustomButton


class QColorButton(QCustomButton):
    def __init__(self, text: str, color: str):
        super().__init__()
        self.setText(text)
        hover_color = adjust_brightness(color, 15)
        pressed_color = adjust_brightness(color, -15)
        disabled_color = adjust_brightness(color, -30)
        self.setStyleSheet(
            """
            QPushButton {
                background-color: %s;
                color: white;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: %s;
            }
            QPushButton:pressed {
                background-color: %s;
            }
            QPushButton:disabled {
                background-color: %s;
            }
            """
            % (color, hover_color, pressed_color, disabled_color)
        )

    def setText(self, text: str):
        super().setText(f" {text}")
