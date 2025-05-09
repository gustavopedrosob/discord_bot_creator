import qtawesome
from PySide6.QtCore import QCoreApplication, Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QFormLayout,
    QSpacerItem,
    QSizePolicy,
)
from extra_qwidgets.fluent_widgets.theme_responsive_tool_button import (
    ThemeResponsiveToolButton,
)
from extra_qwidgets.utils import colorize_icon
from qfluentwidgets import ComboBox, PlainTextEdit

from widgets.channel_dialog import ChannelDialog
from widgets.custom_button import ColoredPushButton

translate = QCoreApplication.translate


class GroupView:
    def __init__(self):
        self.window = QDialog()
        self.window.setWindowFlags(
            self.window.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint
        )
        self.window.setWindowIcon(QIcon("source/icons/window-icon.svg"))
        self.window.setMinimumSize(800, 600)
        self.window.resize(1000, 800)

        self.channel_pick_dialog = ChannelDialog()

        self.welcome_message_channels = ComboBox()
        self.welcome_message_textedit = PlainTextEdit()
        self.welcome_message_textedit.setMaximumHeight(300)
        self.welcome_message_pick_button = ThemeResponsiveToolButton(
            qtawesome.icon("fa6s.list")
        )
        self.welcome_message_pick_button.setIconSize(QSize(19, 19))

        self.goodbye_message_channels = ComboBox()
        self.goodbye_message_textedit = PlainTextEdit()
        self.goodbye_message_textedit.setMaximumHeight(300)
        self.goodbye_message_pick_button = ThemeResponsiveToolButton(
            qtawesome.icon("fa6s.list")
        )
        self.goodbye_message_pick_button.setIconSize(QSize(19, 19))

        self.save_button = ColoredPushButton("#3DCC61", self.window)
        self.save_button.setText(translate("MessageWindow", "Confirm and save"))
        self.save_button.setIcon(
            colorize_icon(qtawesome.icon("fa6s.floppy-disk"), "#FFFFFF")
        )

        self.setup_layout()

    def setup_layout(self):
        main_layout = QFormLayout()
        main_layout.addRow(
            QLabel(translate("GroupWindow", "Welcome message:")),
        )
        welcome_message_channel_layout = QHBoxLayout()
        welcome_message_channel_layout.addWidget(
            self.welcome_message_channels, stretch=1
        )
        welcome_message_channel_layout.addWidget(self.welcome_message_pick_button)
        main_layout.addRow(
            translate("GroupWindow", "Channel:"), welcome_message_channel_layout
        )
        main_layout.addRow(
            QLabel(translate("GroupWindow", "Message:")), self.welcome_message_textedit
        )
        main_layout.addRow(QLabel(translate("GroupWindow", "Goodbye message:")))
        goodbye_message_channel_layout = QHBoxLayout()
        goodbye_message_channel_layout.addWidget(
            self.goodbye_message_channels, stretch=1
        )
        goodbye_message_channel_layout.addWidget(self.goodbye_message_pick_button)
        main_layout.addRow(
            translate("GroupWindow", "Channel:"), goodbye_message_channel_layout
        )
        main_layout.addRow(
            translate("GroupWindow", "Message:"), self.goodbye_message_textedit
        )
        main_layout.addItem(
            QSpacerItem(
                0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
        )
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(
            self.save_button, alignment=Qt.AlignmentFlag.AlignRight
        )
        main_layout.addItem(buttons_layout)
        self.window.setLayout(main_layout)
