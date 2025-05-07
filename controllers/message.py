import typing

from PySide6.QtCore import QPoint
from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QCheckBox,
)
from emojis.db import Emoji
from qfluentwidgets import TransparentToolButton, MessageBox, LineEdit, ListWidget

from core.database import Database
from core.translator import Translator
from models.message import Message
from models.reaction import MessageReaction
from models.reply import MessageReply
from views.messages import MessageView
from widgets.listbox import QListBox


class MessageController:
    def __init__(self, database: Database):
        self.view = MessageView()
        self.database = database
        self.current_message: typing.Optional[Message] = None
        self.setup_binds()

    def setup_binds(self):
        self.__bind_emoji_button(
            self.view.listbox_reactions.emote_button(),
            self.view.listbox_reactions.line_edit(),
        )
        self.__bind_emoji_button(
            self.view.listbox_replies.emote_button(),
            self.view.listbox_replies.line_edit(),
        )
        self.view.listbox_replies.add_button().clicked.connect(
            lambda: self.insert_on_listbox(
                self.view.listbox_replies, self.view.listbox_replies.line_edit()
            )
        )
        self.view.confirm.clicked.connect(self.on_confirm)
        self.view.confirm_and_save.clicked.connect(lambda: self.on_confirm(True))
        self.view.del_checkbox.checkStateChanged.connect(self.__del_checked)
        self.view.author_checkbox.checkStateChanged.connect(self.__author_checked)
        self.view.listbox_reactions.add_button().clicked.connect(
            lambda: self.insert_on_listbox(
                self.view.listbox_reactions, self.view.listbox_reactions.line_edit()
            )
        )

    def __raise_emoji_popup(self, point: QPoint, line_edit: LineEdit):
        def append_emoji(emoji: Emoji):
            return line_edit.insert(emoji.emoji)

        self.view.window.setCursor(Qt.CursorShape.WaitCursor)
        emoji_picker = self.view.emoji_picker_popup.emoji_picker()
        emoji_picker.picked.connect(append_emoji)
        emoji_picker.reset()
        self.view.emoji_picker_popup.move(
            point.x() - self.view.emoji_picker_popup.width(),
            point.y() - self.view.emoji_picker_popup.height(),
        )
        self.view.emoji_picker_popup.exec()
        self.view.emoji_picker_popup.hideEvent = emoji_picker.picked.disconnect(
            append_emoji
        )
        self.view.window.setCursor(Qt.CursorShape.ArrowCursor)

    def is_name_valid(self):
        if self.current_message:
            if self.get_name() == self.current_message.name:
                return True
        return self.get_name() not in self.database.message_names()

    def __bind_emoji_button(
        self,
        emote_button: TransparentToolButton,
        line_edit: LineEdit,
    ):
        emote_button.clicked.connect(
            lambda: self.__raise_emoji_popup(
                emote_button.mapToGlobal(QPoint(0, 0)), line_edit
            )
        )

    def on_confirm(self, save: bool = False):
        if not self.is_name_valid():
            title = Translator.translate("MessageWindow", "Name already exists")
            text = Translator.translate(
                "MessageWindow",
                "You can't set a message with a name that already exists.",
            )
            message_box = MessageBox(title, text, self.view.window)
            message_box.exec()
        else:
            if self.current_message is None:
                self.accepted_new_message()
            else:
                self.accepted_edit_selected_message()
            if save:
                self.view.window.done(2)
            else:
                self.view.window.accept()

    def get_name(self):
        message_name = self.view.name_entry.text()
        if (
            message_name == ""
            and self.current_message
            and self.current_message.name != ""
        ):
            message_name = self.current_message.name
        elif message_name == "":
            message_name = Translator.translate("MessageWindow", "Message {}").format(
                self.database.new_message_id()
            )
        return message_name

    def __del_checked(self, check_state: int):
        author_checkbox = self.view.group_where_react.findChild(QCheckBox, "author")
        author_checkbox.setDisabled(check_state == Qt.CheckState.Checked)

    def __author_checked(self, check_state: int):
        del_checkbox = self.view.group_pin_or_del.findChild(QCheckBox, "delete")
        del_checkbox.setDisabled(check_state == Qt.CheckState.Checked)

    @staticmethod
    def insert_on_listbox(listbox: QListBox, text_edit: LineEdit):
        """Insere um valor na listbox especificada e apaga o conteúdo da entry especificada"""
        text = text_edit.text()
        if text:
            listbox.add_item(text)
            text_edit.clear()

    @staticmethod
    def remove_selected_on_listbox(listbox: ListWidget):
        """remove um item selecionado na listbox"""
        for item in listbox.selectedItems():
            listbox.takeItem(listbox.indexFromItem(item).row())

    def get_message(self, message_id: typing.Optional[int] = None) -> Message:
        message = Message(
            name=self.get_name(),
            pin_or_del=self.view.group_pin_or_del.getCheckedName(),
            kick_or_ban=self.view.group_kick_or_ban.getCheckedName(),
            where_reply=self.view.group_where_reply.getCheckedName(),
            where_reaction=self.view.group_where_react.getCheckedName(),
            delay=self.view.delay.value(),
        )
        if message_id:
            message.id = message_id
        else:
            message.id = self.database.new_message_id()
        return message

    def get_replies(self, message_id: int) -> list[MessageReply]:
        return [
            MessageReply(message_id=message_id, text=i)
            for i in self.view.listbox_replies.get_items_text()
        ]

    def get_reactions(self, message_id: int) -> list[MessageReaction]:
        return [
            MessageReaction(message_id=message_id, reaction=i)
            for i in self.view.listbox_reactions.get_items_text()
        ]

    def accepted_edit_selected_message(self):
        message_id = self.current_message.id
        self.database.delete(self.current_message)
        message = self.get_message(message_id=message_id)
        self.database.add(message)
        self.__add_objects_to_database(message)
        self.current_message = message

    def accepted_new_message(self):
        message = self.get_message()
        self.database.add(message)
        self.__add_objects_to_database(message)
        self.current_message = message

    def __add_objects_to_database(self, message: Message):
        self.database.add_all(self.view.listbox_conditions.get_data(message.id))
        self.database.add_all(self.get_replies(message.id))
        self.database.add_all(self.get_reactions(message.id))

    def reset(self):
        """Resets the window's field."""
        self.current_message = None
        self.view.name_entry.setText("")
        self.view.listbox_replies.reset()
        self.view.listbox_reactions.reset()
        self.view.listbox_conditions.reset()

        for group in (
            self.view.group_pin_or_del,
            self.view.group_kick_or_ban,
            self.view.group_where_reply,
            self.view.group_where_react,
        ):
            group.reset()

    def config(self, message: typing.Optional[Message] = None):
        """Resets the window and setup fields by data parameter."""
        self.reset()
        self.current_message = message
        if message:
            self.view.name_entry.setText(message.name)
            self.view.delay.setValue(message.delay)
            for reply in message.replies:
                self.view.listbox_replies.add_item(reply.text)
            for reaction in message.reactions:
                self.view.listbox_reactions.add_item(reaction.reaction)
            self.view.listbox_conditions.load(message.conditions)
            self.view.group_pin_or_del.checkByName(message.pin_or_del)
            self.view.group_kick_or_ban.checkByName(message.kick_or_ban)
            self.view.group_where_reply.checkByName(message.where_reply)
            self.view.group_where_react.checkByName(message.where_reaction)
        self.view.name_entry.setPlaceholderText(self.get_name())
