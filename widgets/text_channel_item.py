from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem
from discord import TextChannel
from extra_qwidgets.utils import get_awesome_icon


class TextChannelItem(QStandardItem):
    def __init__(self, channel: TextChannel):
        super().__init__(channel.name)
        self.setIcon(get_awesome_icon("hashtag"))
        self.setData(channel.id, Qt.ItemDataRole.UserRole)
        self.setEditable(False)
