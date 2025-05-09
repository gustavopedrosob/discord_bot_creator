import qtawesome
from PySide6.QtCore import Qt
from discord import TextChannel
from extra_qwidgets.widgets.theme_responsive_standard_item import (
    QThemeResponsiveStandardItem,
)


class TextChannelItem(QThemeResponsiveStandardItem):
    def __init__(self, channel: TextChannel):
        super().__init__(channel.name)
        self.setIcon(qtawesome.icon("fa6s.hashtag"))
        self.setData(channel.id, Qt.ItemDataRole.UserRole)
        self.setEditable(False)
