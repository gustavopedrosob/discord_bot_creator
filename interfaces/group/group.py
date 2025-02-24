from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtGui import QIcon, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QDialog, QHBoxLayout, QTreeView, QHeaderView
from discord import VoiceChannel, TextChannel
from extra_qwidgets.utils import get_awesome_icon

translate = QCoreApplication.translate


class TextChannelItem(QStandardItem):
    def __init__(self, channel: TextChannel):
        super().__init__(channel.name)
        self.setIcon(get_awesome_icon("hashtag"))


class VoiceChannelItem(QStandardItem):
    def __init__(self, channel: VoiceChannel):
        super().__init__(channel.name)
        self.setIcon(get_awesome_icon("volume-high"))


class GroupWindow(QDialog):
    def __init__(
        self,
        name: str,
        text_channels: list[TextChannel],
        voice_channels: list[VoiceChannel],
    ):
        super().__init__()
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        self.setWindowIcon(QIcon("source/icons/window-icon.svg"))
        self.setMinimumSize(800, 600)
        self.resize(1000, 800)
        self.setWindowTitle(translate("GroupWindow", "Group {}").format(name))

        main_layout = QHBoxLayout()

        self.channels_model = QStandardItemModel()
        self.channels_treeview = QTreeView()
        self.channels_treeview.setModel(self.channels_model)

        main_layout.addWidget(self.channels_treeview)

        self.setLayout(main_layout)
        self.update_channels(text_channels, voice_channels)

    def update_channels(
        self, text_channels: list[TextChannel], voice_channels: list[VoiceChannel]
    ):
        self.channels_model.clear()
        self.channels_model.setHorizontalHeaderLabels(
            [translate("GroupWindow", "Channels")]
        )
        text_item = QStandardItem(translate("GroupWindow", "Text channels"))
        text_item.appendRows([TextChannelItem(tc) for tc in text_channels])
        self.channels_model.appendRow(text_item)
        voice_item = QStandardItem(translate("GroupWindow", "Voice channels"))
        voice_item.appendRows([VoiceChannelItem(vc) for vc in voice_channels])
        self.channels_model.appendRow(voice_item)
