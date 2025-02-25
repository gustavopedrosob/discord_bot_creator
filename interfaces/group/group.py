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

from interfaces.classes.custom_button import QCustomButton

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


class GroupWindow(QDialog):
    def __init__(
        self,
        name: str,
        text_channels: list[TextChannel],
        voice_channels: list[VoiceChannel],
        welcome_message_channel: typing.Optional[
            typing.Union[TextChannel, VoiceChannel]
        ] = None,
        welcome_message: typing.Optional[str] = None,
    ):
        super().__init__()
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        self.setWindowIcon(QIcon("source/icons/window-icon.svg"))
        self.setMinimumSize(800, 600)
        self.resize(1000, 800)
        self.setWindowTitle(translate("GroupWindow", "Group {}").format(name))

        if welcome_message_channel is None:
            welcome_message_channel = translate("GroupWindow", "Undefined")
            self.welcome_message_channel = None
        else:
            self.welcome_message_channel = welcome_message_channel.id
            welcome_message_channel = welcome_message_channel.name

        self.text_item = QStandardItem(translate("GroupWindow", "Text channels"))
        self.voice_item = QStandardItem(translate("GroupWindow", "Voice channels"))

        self.channels_model = QStandardItemModel()
        self.channels_treeview = QTreeView()
        self.channels_treeview.setModel(self.channels_model)
        self.set_welcome_message_channel_button = QCustomButton(
            translate("GroupWindow", "Set welcome message channel")
        )
        self.welcome_message_channel_label = QLabel()
        self.welcome_message_textedit_label = QLabel(
            translate("GroupWindow", "Welcome message:")
        )
        self.welcome_message_textedit = QResponsiveTextEdit()
        self.welcome_message_textedit.setMaximumHeight(300)
        if welcome_message:
            self.welcome_message_textedit.insertPlainText(welcome_message)
        self.save_button = QColorButton(
            translate("MessageWindow", "Confirm and save"), "#3DCC61"
        )
        self.save_button.setIcon(
            colorize_icon(get_awesome_icon("floppy-disk"), "#FFFFFF")
        )
        self.save_button.clicked.connect(self.accept)

        self.update_welcome_message_channel(welcome_message_channel)
        self.update_channels(text_channels, voice_channels)
        self.setup_layout()
        self.setup_binds()

    def setup_binds(self):
        self.set_welcome_message_channel_button.clicked.connect(
            self.select_welcome_message
        )

    def select_welcome_message(self):
        selection = self.channels_treeview.selectedIndexes()
        if selection:
            selected = self.channels_model.itemFromIndex(selection[0])
            if selected not in (self.text_item, self.voice_item):
                self.update_welcome_message_channel(selected.text())
                self.welcome_message_channel = selected.data(Qt.ItemDataRole.UserRole)

    def update_welcome_message_channel(self, welcome_message_channel: str):
        self.welcome_message_channel_label.setText(
            translate("GroupWindow", "Welcome message channel: {}").format(
                welcome_message_channel
            )
        )

    def update_channels(
        self, text_channels: list[TextChannel], voice_channels: list[VoiceChannel]
    ):
        self.channels_model.clear()
        self.channels_model.setHorizontalHeaderLabels(
            [translate("GroupWindow", "Channels")]
        )
        self.text_item.appendRows([TextChannelItem(tc) for tc in text_channels])
        self.channels_model.appendRow(self.text_item)
        self.voice_item.appendRows([VoiceChannelItem(vc) for vc in voice_channels])
        self.channels_model.appendRow(self.voice_item)

    def get_data(self) -> dict:
        return dict(
            welcome_message=self.welcome_message_textedit.toPlainText(),
            welcome_message_channel=self.welcome_message_channel,
        )

    def setup_layout(self):
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        left_layout.addWidget(self.channels_treeview)
        left_layout.addWidget(self.welcome_message_channel_label)
        left_layout.addWidget(self.set_welcome_message_channel_button)
        right_layout.addWidget(self.welcome_message_textedit_label)
        right_layout.addWidget(self.welcome_message_textedit)
        right_layout.addStretch()
        right_layout.addWidget(self.save_button)
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)
