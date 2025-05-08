from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from qfluentwidgets import SplashScreen
from qfluentwidgets.components.widgets.frameless_window import FramelessWindow


class LoadingView:
    def __init__(self):
        self.window = FramelessWindow()
        self.window.setWindowTitle("Discord Bot Creator")
        self.window.setWindowIcon(QIcon("source/icons/window-icon.svg"))
        self.window.setFixedSize(400, 600)

        self.splash = SplashScreen(QIcon("source/icons/icon.svg"), self.window)
        self.splash.setIconSize(QSize(192, 192))
        for window in (self.window, self.splash):
            window.titleBar.minBtn.hide()
            window.titleBar.maxBtn.hide()
            window.titleBar.closeBtn.hide()

        self.splash.show()
        self.window.show()
