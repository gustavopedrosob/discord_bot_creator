import typing

from PySide6.QtCore import Qt, QCoreApplication
from discord import TextChannel, VoiceChannel

from core.interactions import interactions
from views.group.group import GroupView, TextChannelItem, VoiceChannelItem

translate = QCoreApplication.translate

class GroupController:
    def __init__(self):
        self.view = GroupView()
        self.welcome_message_channel = None
        self.group_id = None
        self.setup_binds()

    def setup_binds(self):
        self.view.set_welcome_message_channel_button.clicked.connect(
            self.select_welcome_message_channel
        )
        self.view.unset_welcome_message_channel_button.clicked.connect(
            self.unselect_welcome_message_channel
        )
        self.view.save_button.clicked.connect(self.view.window.accept)
        self.view.window.accepted.connect(self.save_group)

    def select_welcome_message_channel(self):
        selection = self.view.channels_treeview.selectedIndexes()
        if selection:
            selected = self.view.channels_model.itemFromIndex(selection[0])
            if selected not in (self.view.text_item, self.view.voice_item):
                self.update_welcome_message_channel(selected.text())
                self.welcome_message_channel = selected.data(Qt.ItemDataRole.UserRole)

    def unselect_welcome_message_channel(self):
        self.update_welcome_message_channel(translate("GroupWindow", "Undefined"))
        self.welcome_message_channel = None

    def update_welcome_message_channel(self, welcome_message_channel: str):
        self.view.welcome_message_channel_label.setText(
            translate("GroupWindow", "Welcome message channel: {}").format(
                welcome_message_channel
            )
        )

    def update_channels(
        self, text_channels: list[TextChannel], voice_channels: list[VoiceChannel]
    ):
        self.view.channels_model.clear()
        self.view.channels_model.setHorizontalHeaderLabels(
            [translate("GroupWindow", "Channels")]
        )
        self.view.text_item.appendRows([TextChannelItem(tc) for tc in text_channels])
        self.view.channels_model.appendRow(self.view.text_item)
        self.view.voice_item.appendRows([VoiceChannelItem(vc) for vc in voice_channels])
        self.view.channels_model.appendRow(self.view.voice_item)
        self.view.channels_treeview.expandAll()

    def get_data(self) -> dict:
        return dict(
            welcome_message=self.view.welcome_message_textedit.toPlainText(),
            welcome_message_channel=self.welcome_message_channel,
        )

    def save_group(self):
        data = self.get_data()
        groups = interactions.get("groups")
        groups[str(self.group_id)] = data

    def reset(self):
        self.view.welcome_message_textedit.clear()

    def config(self,
        group_id: str,
        name: str,
        text_channels: list[TextChannel],
        voice_channels: list[VoiceChannel],
        welcome_message_channel: typing.Optional[
            typing.Union[TextChannel, VoiceChannel]
        ] = None,
        welcome_message: typing.Optional[str] = None,
    ):
        self.reset()
        self.group_id = group_id
        self.view.window.setWindowTitle(translate("GroupWindow", "Group {}").format(name))
        if welcome_message_channel is None:
            welcome_message_channel = translate("GroupWindow", "Undefined")
            self.welcome_message_channel = None
        else:
            self.welcome_message_channel = welcome_message_channel.id
            welcome_message_channel = welcome_message_channel.name

        if welcome_message:
            self.view.welcome_message_textedit.insertPlainText(welcome_message)
        self.update_welcome_message_channel(welcome_message_channel)
        self.update_channels(text_channels, voice_channels)