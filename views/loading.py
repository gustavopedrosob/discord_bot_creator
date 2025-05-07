from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from qfluentwidgets import SplashScreen
from qfluentwidgets.components.widgets.frameless_window import FramelessWindow


class LoadingView:
    def __init__(self):
        self.window = FramelessWindow()
        self.window.setWindowTitle("Discord Bot Creator")
        self.window.setFixedSize(700, 600)

        self.splash = SplashScreen(QIcon("source/icons/icon.svg"), self.window)
        self.splash.setIconSize(QSize(128, 128))
        self.splash.show()

        self.window.show()
