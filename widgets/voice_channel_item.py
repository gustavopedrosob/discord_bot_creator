from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem
from discord import VoiceChannel
from extra_qwidgets.utils import get_awesome_icon


class VoiceChannelItem(QStandardItem):
    def __init__(self, channel: VoiceChannel):
        super().__init__(channel.name)
        self.setIcon(get_awesome_icon("volume-high"))
        self.setData(channel.id, Qt.ItemDataRole.UserRole)
        self.setEditable(False)
