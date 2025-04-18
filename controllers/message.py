import typing

from PySide6.QtCore import QPoint
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QMessageBox, QHBoxLayout, QLineEdit, QTextEdit, QCheckBox
from emojis import emojis
from emojis.db import Emoji
from extra_qwidgets.utils import get_awesome_icon
from extra_qwidgets.widgets import QResponsiveTextEdit, QThemeResponsiveButton

from core.interactions import interactions
from core.translator import Translator
from views.classes.emoji_picker import QEmojiPickerPopup
from views.messages.listbox import QListBox
from views.messages.messages import MessageView


class MessageController:
    def __init__(self):
        self.view = MessageView()
        self.current_message = None
        self.emoji_picker_popup = None
        self.setup_binds()

    def setup_binds(self):
        self.__add_emoji_button(
            self.view.listbox_reactions.entry_layout(), self.view.reactions_line_edit
        )
        self.__add_emoji_button(
            self.view.listbox_messages.entry_layout(), self.view.messages_line_edit
        )
        self.__add_emoji_button(self.view.listbox_replies.entry_layout(), self.view.replies_line_edit)
        self.view.listbox_messages.add_button().clicked.connect(
            lambda: self.insert_on_listbox(self.view.listbox_messages, self.view.messages_line_edit)
        )
        self.view.listbox_conditions.add_button().clicked.connect(self.__on_add_condition)
        self.view.listbox_replies.add_button().clicked.connect(
            lambda: self.insert_on_listbox(self.view.listbox_replies, self.view.replies_line_edit)
        )
        self.view.confirm.clicked.connect(self.on_confirm)
        self.view.confirm_and_save.clicked.connect(lambda: self.on_confirm(True))
        self.view.del_checkbox.checkStateChanged.connect(self.__del_checked)
        self.view.author_checkbox.checkStateChanged.connect(self.__author_checked)
        self.view.listbox_reactions.add_button().clicked.connect(
            lambda: self.insert_on_listbox(self.view.listbox_reactions, self.view.reactions_line_edit)
        )

    def __raise_emoji_popup(self, point: QPoint, line_edit: QTextEdit):
        def append_emoji(emoji: Emoji):
            return line_edit.insertPlainText(emoji.emoji)

        self.view.window.setCursor(Qt.CursorShape.WaitCursor)
        if self.emoji_picker_popup is None:
            self.emoji_picker_popup = QEmojiPickerPopup()
        emoji_picker = self.emoji_picker_popup.emoji_picker()
        emoji_picker.picked.connect(append_emoji)
        emoji_picker.reset()
        self.emoji_picker_popup.move(point.x() - 500, point.y() - 500)
        self.emoji_picker_popup.exec()
        self.emoji_picker_popup.hideEvent = emoji_picker.picked.disconnect(append_emoji)
        self.view.window.setCursor(Qt.CursorShape.ArrowCursor)

    def _add_condition(self, condition: str):
        translated_condition = self.view.translated_conditions[condition]
        item = QListWidgetItem()
        item.setText(translated_condition)
        item.setData(Qt.ItemDataRole.UserRole, condition)
        self.view.listbox_conditions.add_item(item)

    def __on_add_condition(self):
        index = self.view.conditions_combobox.currentIndex()
        condition = self.view.conditions_combobox.itemData(index, Qt.ItemDataRole.UserRole)
        if condition not in self.view.listbox_conditions.get_items_userdata():
            self._add_condition(condition)

    def is_name_valid(self):
        return self.get_name() not in interactions.message_names() and self.get_name() != self.current_message

    def __add_emoji_button(
        self, layout: QHBoxLayout, line_edit: typing.Union[QLineEdit, QTextEdit]
    ):
        emote_button = QThemeResponsiveButton()
        emote_button.setIcon(get_awesome_icon("face-smile"))
        emote_button.setFlat(True)
        layout.addWidget(emote_button, alignment=Qt.AlignmentFlag.AlignTop)
        emote_button.clicked.connect(
            lambda: self.__raise_emoji_popup(
                emote_button.mapToGlobal(QPoint(0, 0)), line_edit
            )
        )

    def on_confirm(self, save: bool = False):
        if not self.is_name_valid():
            message_box = QMessageBox()
            message_box.setWindowTitle(
                Translator.translate("MessageWindow", "Name already exists")
            )
            message_box.setWindowIcon(QIcon("source/icons/window-icon.svg"))
            message_box.setText(
                Translator.translate(
                    "MessageWindow",
                    "You can't set a message with a name that already exists.",
                )
            )
            message_box.exec()
        elif self.__has_opposite_conditions():
            message_box = QMessageBox()
            message_box.setWindowTitle(
                Translator.translate("MessageWindow", "Opposite conditions")
            )
            message_box.setWindowIcon(QIcon("source/icons/window-icon.svg"))
            message_box.setText(
                Translator.translate(
                    "MessageWindow",
                    "You can't have opposite conditions, please remove them.",
                )
            )
            message_box.exec()
        else:
            if self.current_message is None:
                self.accepted_new_message(self.get_name(), self.get_data())
            else:
                self.accepted_edit_selected_message(self.current_message, self.get_name(), self.get_data())
            if save:
                self.view.window.done("save")
            else:
                self.view.window.accept()

    def __has_opposite_conditions(self) -> bool:
        conditions = self.view.listbox_conditions.get_items_userdata()
        for condition in conditions:
            opposite_condition = (
                condition[4:] if condition.startswith("not ") else f"not {condition}"
            )
            if opposite_condition in conditions:
                return True
        return False

    def get_name(self):
        return self.view.name_entry.text()

    def __del_checked(self, check_state: int):
        author_checkbox = self.view.group_where_react.findChild(QCheckBox, "author")
        author_checkbox.setDisabled(check_state == Qt.CheckState.Checked)

    def __author_checked(self, check_state: int):
        del_checkbox = self.view.group_pin_or_del.findChild(QCheckBox, "delete")
        del_checkbox.setDisabled(check_state == Qt.CheckState.Checked)

    @staticmethod
    def insert_on_listbox(listbox: QListBox, text_edit: QResponsiveTextEdit):
        """Insere um valor na listbox especificada e apaga o conteúdo da entry especificada"""
        text = text_edit.toPlainText()
        if text:
            listbox.add_item(text)
            text_edit.clear()

    @staticmethod
    def remove_selected_on_listbox(listbox: QListWidget):
        """remove um item selecionado na listbox"""
        for item in listbox.selectedItems():
            listbox.takeItem(listbox.indexFromItem(item).row())

    def get_data(self) -> dict:
        result = {"expected message": self.view.listbox_messages.get_items_text()}
        reply_list = self.view.listbox_replies.get_items_text()
        result["reply"] = list(map(lambda replies: replies.split("¨"), reply_list))
        reactions_list = self.view.listbox_reactions.get_items_text()
        result["reaction"] = list(
            map(lambda reactions: list(emojis.get(reactions)), reactions_list)
        )
        result["conditions"] = self.view.listbox_conditions.get_items_userdata()
        result["pin or del"] = self.view.group_pin_or_del.get_checked_name()
        result["kick or ban"] = self.view.group_kick_or_ban.get_checked_name()
        result["where reply"] = self.view.group_where_reply.get_checked_name()
        result["where reaction"] = self.view.group_where_react.get_checked_name()
        result["delay"] = self.view.delay.value()

        return result

    @staticmethod
    def accepted_edit_selected_message(
        old_message_name: str, new_message_name: str, message_data: dict
    ):
        if not new_message_name:
            new_message_name = old_message_name
        messages: dict = interactions.get("messages")
        messages.pop(old_message_name)
        messages[new_message_name] = message_data

    @staticmethod
    def accepted_new_message(message_name: str, message_data: dict):
        if not message_name:
            message_name = interactions.new_id()
        messages: dict = interactions.get("messages")
        messages[message_name] = message_data

    def reset(self):
        """Resets the window's field."""
        self.view.name_entry.setText("")
        self.view.listbox_messages.reset()
        self.view.listbox_replies.reset()
        self.view.listbox_reactions.reset()
        self.view.listbox_conditions.reset()

        for group in (self.view.group_pin_or_del, self.view.group_kick_or_ban, self.view.group_where_reply, self.view.group_where_react):
            group.reset()

    def config(self, name: str, data: dict):
        """Resets the window and setup fields by data parameter."""
        self.reset()
        self.view.name_entry.setText(name)
        self.view.delay.setValue(data["delay"])
        self.view.listbox_messages.add_items(data["expected message"])
        for reply in data["reply"]:
            self.view.listbox_replies.add_item("¨".join(reply))
        for reaction in data["reaction"]:
            self.view.listbox_reactions.add_item("".join(reaction))
        for condition in data["conditions"]:
            self._add_condition(condition)
        self.view.group_pin_or_del.check_by_name(data["pin or del"])
        self.view.group_kick_or_ban.check_by_name(data["kick or ban"])
        self.view.group_where_reply.check_by_name(data["where reply"])
        self.view.group_where_react.check_by_name(data["where reaction"])