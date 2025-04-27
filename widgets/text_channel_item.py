import qtawesome
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem
from discord import TextChannel


class TextChannelItem(QStandardItem):
    def __init__(self, channel: TextChannel):
        super().__init__(channel.name)
        self.setIcon(qtawesome.icon("fa6s.hashtag"))
        self.setData(channel.id, Qt.ItemDataRole.UserRole)
        self.setEditable(False)
