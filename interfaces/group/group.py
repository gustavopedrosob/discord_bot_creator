from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QListWidget, QHBoxLayout

translate = QCoreApplication.translate


class GroupWindow(QDialog):
    def __init__(self, name: str):
        super().__init__()
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        self.setWindowIcon(QIcon("source/icons/window-icon.svg"))
        self.setMinimumSize(800, 600)
        self.resize(1000, 800)
        self.setWindowTitle(translate("GroupWindow", "Group {}").format(name))

        main_layout = QHBoxLayout()

        self.channels_list = QListWidget()

        main_layout.addWidget(self.channels_list)

        self.setLayout(main_layout)

    def update_channels(self, channels: list[str]):
        self.channels_list.clear()
        self.channels_list.addItems(channels)
