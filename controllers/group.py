import typing

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QComboBox, QDialog
from discord import Guild

from core.database import Database
from models.group import Group
from views.group import GroupView

translate = QCoreApplication.translate


class GroupController:
    def __init__(self, database: Database):
        self.view = GroupView()
        self.database = database
        self.group: typing.Optional[Group] = None
        self.discord_group: typing.Optional[Guild] = None
        self.setup_binds()

    def setup_binds(self):
        self.view.save_button.clicked.connect(self.view.window.accept)
        self.view.welcome_message_pick_button.clicked.connect(
            lambda: self.on_channel_pick_button_pressed(
                self.view.welcome_message_channels
            )
        )
        self.view.goodbye_message_pick_button.clicked.connect(
            lambda: self.on_channel_pick_button_pressed(
                self.view.goodbye_message_channels
            )
        )
        self.view.window.accepted.connect(self.save_group)

    def on_channel_pick_button_pressed(self, combobox: QComboBox):
        dialog_result = self.view.channel_pick_dialog.exec()
        if dialog_result == QDialog.DialogCode.Accepted:
            self.set_combobox_current_channel(
                self.view.channel_pick_dialog.get_selected_channel_id(), combobox
            )

    @staticmethod
    def set_combobox_current_channel(channel_id: int, combobox: QComboBox):
        index = combobox.findData(channel_id)
        combobox.setCurrentIndex(index)

    def get_data(self) -> Group:
        return Group(
            id=self.discord_group.id,
            welcome_message=self.view.welcome_message_textedit.toPlainText(),
            welcome_message_channel=self.view.welcome_message_channels.currentData(),
            goodbye_message=self.view.goodbye_message_textedit.toPlainText(),
            goodbye_message_channel=self.view.goodbye_message_channels.currentData(),
        )

    def save_group(self):
        self.database.merge(self.get_data())

    def reset(self):
        self.view.welcome_message_textedit.setPlainText("")
        self.view.goodbye_message_textedit.setPlainText("")
        self.view.welcome_message_channels.clear()
        self.view.goodbye_message_channels.clear()
        self.view.channel_pick_dialog.reset()

    def update_channels(self, discord_group: Guild):
        self.view.welcome_message_channels.addItem(
            translate("GroupWindow", "(None)"), None
        )
        self.view.goodbye_message_channels.addItem(
            translate("GroupWindow", "(None)"), None
        )
        for channel in discord_group.text_channels + discord_group.voice_channels:
            self.view.welcome_message_channels.addItem(
                channel.name, userData=channel.id
            )
            self.view.goodbye_message_channels.addItem(
                channel.name, userData=channel.id
            )
        self.view.channel_pick_dialog.update_channels(discord_group)

    def config(
        self,
        discord_group: Guild,
        group: typing.Optional[Group] = None,
    ):
        self.reset()
        self.update_channels(discord_group)
        self.discord_group = discord_group
        if group:
            self.group = group
            self.set_combobox_current_channel(
                group.welcome_message_channel, self.view.welcome_message_channels
            )
            self.view.welcome_message_textedit.insertPlainText(
                group.welcome_message if group.welcome_message else ""
            )
            self.set_combobox_current_channel(
                group.goodbye_message_channel, self.view.goodbye_message_channels
            )
            self.view.goodbye_message_textedit.insertPlainText(
                group.goodbye_message if group.goodbye_message else ""
            )
        else:
            self.group = Group(id=discord_group.id)
        self.view.window.setWindowTitle(
            translate("GroupWindow", "Group {}").format(discord_group.name)
        )
