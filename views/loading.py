from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QColor, QPainter
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QVBoxLayout,
    QApplication,
    QPushButton,
)
import qtawesome as qta
from qfluentwidgets.components.widgets.frameless_window import FramelessWindow


class LoadingView:
    icon_path = Path(__file__).parent.parent / "source/icons/icon.svg"
    window_icon_path = Path(__file__).parent.parent / "source/icons/window-icon.svg"
    spin_button_size = QSize(40, 40)

    def __init__(self):
        self.window = FramelessWindow()
        self.window.setWindowTitle("Discord Bot Creator")
        self.window.setWindowIcon(QIcon(str(self.window_icon_path)))
        self.window.setFixedSize(400, 500)
        self.window.titleBar.minBtn.hide()
        self.window.titleBar.maxBtn.hide()
        self.window.titleBar.closeBtn.hide()
        self.window.setResizeEnabled(False)

        self.svg = QSvgWidget(str(self.icon_path))
        self.svg.setFixedSize(192, 192)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 160))

        self.svg.setGraphicsEffect(shadow)

        self.spin_button = QPushButton()
        self.spin_button.setFixedSize(self.spin_button_size)
        self.spin_button.setIconSize(self.spin_button_size)
        self.spin_button.setFlat(True)
        self.spin_button.setEnabled(False)
        animation = qta.Spin(self.spin_button)
        spinner_icon = qta.icon("fa5s.spinner", color="gray", animation=animation)
        self.spin_button.setIcon(spinner_icon)

        self._setup_layout()
        self.window.show()

    def _setup_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(
            self.svg,
            alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
        )
        layout.addWidget(
            self.spin_button,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        self.window.setLayout(layout)


if __name__ == "__main__":
    app = QApplication([])
    window = LoadingView()
    app.exec()
