import typing

from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtGui import QIcon, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QTreeView,
    QVBoxLayout,
    QLabel,
)
from discord import VoiceChannel, TextChannel
from extra_qwidgets.utils import get_awesome_icon, colorize_icon
from extra_qwidgets.widgets import QResponsiveTextEdit, QColorButton

from views.classes.custom_button import QCustomButton

translate = QCoreApplication.translate


class TextChannelItem(QStandardItem):
    def __init__(self, channel: TextChannel):
        super().__init__(channel.name)
        self.setIcon(get_awesome_icon("hashtag"))
        self.setData(channel.id, Qt.ItemDataRole.UserRole)


class VoiceChannelItem(QStandardItem):
    def __init__(self, channel: VoiceChannel):
        super().__init__(channel.name)
        self.setIcon(get_awesome_icon("volume-high"))
        self.setData(channel.id, Qt.ItemDataRole.UserRole)


class GroupView:
    def __init__(self):
        self.window = QDialog()
        self.window.setWindowFlags(
            self.window.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint
        )
        self.window.setWindowIcon(QIcon("source/icons/window-icon.svg"))
        self.window.setMinimumSize(800, 600)
        self.window.resize(1000, 800)

        self.text_item = QStandardItem(translate("GroupWindow", "Text channels"))
        self.voice_item = QStandardItem(translate("GroupWindow", "Voice channels"))

        self.channels_model = QStandardItemModel()
        self.channels_treeview = QTreeView()
        self.channels_treeview.setModel(self.channels_model)
        self.set_welcome_message_channel_button = QCustomButton(
            translate("GroupWindow", "Set welcome message channel")
        )
        self.unset_welcome_message_channel_button = QCustomButton(
            translate("GroupWindow", "Unset welcome message channel")
        )
        self.welcome_message_channel_label = QLabel()
        self.welcome_message_textedit_label = QLabel(
            translate("GroupWindow", "Welcome message:")
        )
        self.welcome_message_textedit = QResponsiveTextEdit()
        self.welcome_message_textedit.setMaximumHeight(300)
        self.save_button = QColorButton(
            translate("MessageWindow", "Confirm and save"), "#3DCC61"
        )
        self.save_button.setIcon(
            colorize_icon(get_awesome_icon("floppy-disk"), "#FFFFFF")
        )

        self.setup_layout()

    def setup_layout(self):
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        for widget in (
            self.channels_treeview,
            self.welcome_message_channel_label,
            self.set_welcome_message_channel_button,
            self.unset_welcome_message_channel_button,
        ):
            left_layout.addWidget(widget)
        right_layout.addWidget(self.welcome_message_textedit_label)
        right_layout.addWidget(self.welcome_message_textedit)
        right_layout.addStretch()
        right_layout.addWidget(self.save_button)
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.window.setLayout(main_layout)
