import typing
from PySide6.QtCore import Qt, QCoreApplication
from discord import Guild
from core.database import Database
from models.group import Group
from views.group.group import GroupView, TextChannelItem, VoiceChannelItem

translate = QCoreApplication.translate


class GroupController:
    def __init__(self, database: Database):
        self.view = GroupView()
        self.database = database
        self.group: typing.Optional[Group] = None
        self.discord_group: typing.Optional[Guild] = None
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
                self.group.welcome_message_channel = selected.data(
                    Qt.ItemDataRole.UserRole
                )

    def unselect_welcome_message_channel(self):
        self.update_welcome_message_channel(translate("GroupWindow", "Undefined"))
        self.group.welcome_message_channel = None

    def update_welcome_message_channel(self, welcome_message_channel: str):
        self.view.welcome_message_channel_label.setText(
            translate("GroupWindow", "Welcome message channel: {}").format(
                welcome_message_channel
            )
        )

    def _get_welcome_message_channel(self):
        return self.discord_group.get_channel(self.group.welcome_message_channel)

    def update_channels(self, group: Guild):
        self.view.channels_model.clear()
        self.view.channels_model.setHorizontalHeaderLabels(
            [translate("GroupWindow", "Channels")]
        )
        self.view.text_item.appendRows(
            [TextChannelItem(tc) for tc in group.text_channels]
        )
        self.view.channels_model.appendRow(self.view.text_item)
        self.view.voice_item.appendRows(
            [VoiceChannelItem(vc) for vc in group.voice_channels]
        )
        self.view.channels_model.appendRow(self.view.voice_item)
        self.view.channels_treeview.expandAll()

    def get_data(self) -> Group:
        welcome_message_channel = self._get_welcome_message_channel()
        return Group(
            id=self.discord_group.id,
            welcome_message=self.view.welcome_message_textedit.toPlainText(),
            welcome_message_channel=(
                welcome_message_channel.id if welcome_message_channel else None
            ),
        )

    def save_group(self):
        session = self.database.get_session()
        session.merge(self.get_data())

    def reset(self):
        self.view.welcome_message_textedit.setPlainText("")
        self.view.text_item.removeRows(0, self.view.text_item.rowCount())
        self.view.voice_item.removeRows(0, self.view.voice_item.rowCount())

    def config(
        self,
        discord_group: Guild,
        group: typing.Optional[Group] = None,
    ):
        self.reset()
        self.discord_group = discord_group
        if group:
            self.group = group
            welcome_message_channel = self._get_welcome_message_channel()
            if group.welcome_message:
                self.view.welcome_message_textedit.insertPlainText(
                    group.welcome_message
                )
            if welcome_message_channel:
                self.update_welcome_message_channel(welcome_message_channel.name)
            else:
                self.update_welcome_message_channel(
                    translate("GroupWindow", "Undefined")
                )
        else:
            self.group = Group(id=discord_group.id)
            self.unselect_welcome_message_channel()
        self.view.window.setWindowTitle(
            translate("GroupWindow", "Group {}").format(discord_group.name)
        )
        self.update_channels(discord_group)
