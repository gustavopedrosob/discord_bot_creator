import qtawesome
from PySide6.QtCore import Qt
from discord import VoiceChannel
from extra_qwidgets.widgets.theme_responsive_standard_item import (
    QThemeResponsiveStandardItem,
)


class VoiceChannelItem(QThemeResponsiveStandardItem):
    def __init__(self, channel: VoiceChannel):
        super().__init__(channel.name)
        self.setIcon(qtawesome.icon("fa6s.volume-high"))
        self.setData(channel.id, Qt.ItemDataRole.UserRole)
        self.setEditable(False)
