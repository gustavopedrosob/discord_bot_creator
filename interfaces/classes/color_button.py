from PySide6.QtWidgets import QPushButton

from core.functions import adjust_brightness


class QColorButton(QPushButton):
    def __init__(self, text: str, color: str):
        super().__init__()
        self.setText(text)
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
            """
            % (color, adjust_brightness(color, 15), adjust_brightness(color, -15))
        )

    def setText(self, text: str):
        super().setText(f" {text}")
