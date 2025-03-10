import typing

from PySide6.QtCore import (
    Qt,
    QCoreApplication,
    QPoint,
    QRegularExpression,
    QMimeData,
)
from PySide6.QtGui import (
    QIcon,
    QRegularExpressionValidator,
    QKeyEvent,
    QValidator,
)
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QDialog,
    QLabel,
    QComboBox,
    QListWidget,
    QSpinBox,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QListWidgetItem,
    QCheckBox,
)
from emojis import emojis
from emojis.db import Emoji
from extra_qwidgets.utils import get_awesome_icon, colorize_icon
from extra_qwidgets.widgets import QThemeResponsiveButton
from extra_qwidgets.widgets.checkboxes import QCheckBoxes
from extra_qwidgets.widgets.collapse_group import QCollapseGroup
from extra_qwidgets.widgets.color_button import QColorButton
from extra_qwidgets.widgets.emoji_picker.emoji_validator import QEmojiValidator
from extra_qwidgets.widgets.resposive_text_edit import QResponsiveTextEdit

from core.interactions import interactions
from interfaces.classes.custom_button import QCustomButton
from interfaces.classes.custom_checkbox import QCustomCheckBox
from interfaces.classes.emoji_picker import QEmojiPickerPopup
from interfaces.messages.listbox import QListBox

translate = QCoreApplication.translate


class QMessageTextEdit(QResponsiveTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMaximumHeight(400)
        self.__validator = None

    def validator(self) -> typing.Optional[QValidator]:
        return self.__validator

    def set_validator(self, validator: QValidator):
        self.__validator = validator

    def insertFromMimeData(self, source: QMimeData):
        if source.hasText():
            text = source.text()
            validator = self.validator()
            if validator and validator.validate(text, 0) not in (
                QValidator.State.Intermediate,
                QValidator.State.Acceptable,
            ):
                return
            mime_data = QMimeData()
            mime_data.setText(source.text())
            super().insertFromMimeData(mime_data)

    def keyPressEvent(self, e: QKeyEvent):
        if e.modifiers() == Qt.KeyboardModifier.NoModifier and e.key() not in (
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter,
            Qt.Key.Key_Backspace,
        ):
            text = self.toPlainText() + e.text()
            validator = self.validator()
            if validator and validator.validate(text, 0) not in (
                QValidator.State.Intermediate,
                QValidator.State.Acceptable,
            ):
                return
            super().keyPressEvent(e)
        else:
            super().keyPressEvent(e)


class MessageWindow:
    def __init__(self, app):
        self.app = app
        self.window = QDialog()
        self.window.setWindowFlags(
            self.window.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint
        )
        self.window.setWindowIcon(QIcon("source/icons/window-icon.svg"))
        self.window.setMinimumSize(800, 600)
        self.window.resize(1000, 800)
        self.window.setWindowTitle(translate("MessageWindow", "Message"))

        self.emoji_picker_popup = None

        left_layout = QVBoxLayout()
        mid_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        self.name_text = QLabel(translate("MessageWindow", "Name"))
        self.name_entry = QLineEdit()
        self.name_entry.setToolTip(
            translate(
                "MessageWindow",
                "The name can include letters (with accents), numbers, and spaces. Example: 'John123'.",
            )
        )
        name_entry_validator = QRegularExpressionValidator(
            QRegularExpression(r"[A-zÀ-ú0-9 ]*")
        )
        self.name_entry.setMaxLength(40)
        self.name_entry.setValidator(name_entry_validator)

        self._translated_conditions = {
            "expected message": translate("Conditions", "expected message"),
            "not expected message": translate("Conditions", "not expected message"),
            "mention bot": translate("Conditions", "mention bot"),
            "not mention bot": translate("Conditions", "not mention bot"),
            "mention someone": translate("Conditions", "mention someone"),
            "not mention someone": translate("Conditions", "not mention someone"),
            "mention everyone": translate("Conditions", "mention everyone"),
            "not mention everyone": translate("Conditions", "not mention everyone"),
            "author is bot": translate("Conditions", "author is bot"),
            "not author is bot": translate("Conditions", "not author is bot"),
            "number in message": translate("Conditions", "number in message"),
            "not number in message": translate("Conditions", "not number in message"),
            "symbols in message": translate("Conditions", "symbols in message"),
            "not symbols in message": translate("Conditions", "not symbols in message"),
            "emojis in message": translate("Conditions", "emojis in message"),
            "not emojis in message": translate("Conditions", "not emojis in message"),
        }

        self.conditions_combobox = QComboBox()
        for condition, translated_condition in self._translated_conditions.items():
            self.conditions_combobox.addItem(translated_condition, condition)

        self.listbox_conditions = QListBox(self.conditions_combobox)
        self.listbox_conditions.add_button().clicked.connect(self.__on_add_condition)
        collapse_conditions = QCollapseGroup(
            translate("MessageWindow", "Conditions"),
            self.listbox_conditions,
        )
        collapse_conditions.setContentsMargins(0, 0, 0, 0)

        emoji_validator = QEmojiValidator()
        reactions_line_edit = QMessageTextEdit()
        reactions_line_edit.set_validator(emoji_validator)
        self.listbox_reactions = QListBox(reactions_line_edit)
        self.listbox_reactions.add_button().clicked.connect(
            lambda: self.insert_on_listbox(self.listbox_reactions, reactions_line_edit)
        )
        self.__add_emoji_button(
            self.listbox_reactions.entry_layout(), reactions_line_edit
        )
        collapse_reactions = QCollapseGroup(
            translate("MessageWindow", "Reactions"),
            self.listbox_reactions,
        )
        collapse_reactions.setContentsMargins(0, 0, 0, 0)

        messages_line_edit = QMessageTextEdit()
        self.listbox_messages = QListBox(messages_line_edit)
        self.listbox_messages.add_button().clicked.connect(
            lambda: self.insert_on_listbox(self.listbox_messages, messages_line_edit)
        )
        self.__add_emoji_button(
            self.listbox_messages.entry_layout(), messages_line_edit
        )
        collapse_messages = QCollapseGroup(
            translate("MessageWindow", "Messages"), self.listbox_messages
        )
        collapse_messages.setContentsMargins(0, 0, 0, 0)

        replies_line_edit = QMessageTextEdit()
        self.listbox_replies = QListBox(replies_line_edit)
        self.listbox_replies.add_button().clicked.connect(
            lambda: self.insert_on_listbox(self.listbox_replies, replies_line_edit)
        )
        self.__add_emoji_button(self.listbox_replies.entry_layout(), replies_line_edit)
        collapse_replies = QCollapseGroup(
            translate("MessageWindow", "Replies"), self.listbox_replies
        )
        collapse_messages.setContentsMargins(0, 0, 0, 0)

        for widget in (
            collapse_conditions,
            collapse_reactions,
            collapse_messages,
            collapse_replies,
        ):
            left_layout.addWidget(widget)

        left_layout.setSpacing(0)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.group_pin_or_del = QCheckBoxes(
            QLabel(translate("MessageWindow", "Action"))
        )
        del_checkbox = QCustomCheckBox("delete", translate("MessageWindow", "Delete"))
        del_checkbox.checkStateChanged.connect(self.__del_checked)
        self.group_pin_or_del.add_checkboxes(
            QCustomCheckBox("pin", translate("MessageWindow", "Pin")), del_checkbox
        )
        right_layout.addWidget(self.group_pin_or_del)

        self.group_kick_or_ban = QCheckBoxes(
            QLabel(translate("MessageWindow", "Penalty"))
        )
        self.group_kick_or_ban.add_checkboxes(
            QCustomCheckBox("kick", translate("MessageWindow", "Kick")),
            QCustomCheckBox("ban", translate("MessageWindow", "Ban")),
        )
        right_layout.addWidget(self.group_kick_or_ban)

        self.group_where_reply = QCheckBoxes(
            QLabel(translate("MessageWindow", "Where reply"))
        )
        self.group_where_reply.add_checkboxes(
            QCustomCheckBox("group", translate("MessageWindow", "Group")),
            QCustomCheckBox("private", translate("MessageWindow", "Private")),
        )
        right_layout.addWidget(self.group_where_reply)

        self.group_where_react = QCheckBoxes(
            QLabel(translate("MessageWindow", "Where react"))
        )
        author_checkbox = QCustomCheckBox(
            "author", translate("MessageWindow", "Author")
        )
        author_checkbox.checkStateChanged.connect(self.__author_checked)
        self.group_where_react.add_checkboxes(
            author_checkbox, QCustomCheckBox("bot", translate("MessageWindow", "Bot"))
        )
        right_layout.addWidget(self.group_where_react)

        delay_label = QLabel(translate("MessageWindow", "Delay"))
        self.delay = QSpinBox()

        confirm = QCustomButton(translate("MessageWindow", "Confirm"))

        confirm_and_save = QColorButton(
            translate("MessageWindow", "Confirm and save"), "#3DCC61"
        )
        confirm_and_save.setAutoDefault(False)
        confirm_and_save.setDefault(False)
        confirm_and_save.setIcon(
            colorize_icon(get_awesome_icon("floppy-disk"), "#FFFFFF")
        )

        for widget in (
            delay_label,
            self.delay,
        ):
            right_layout.addWidget(widget)

        right_layout.addStretch()
        right_layout.addWidget(confirm)
        right_layout.addWidget(confirm_and_save)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addLayout(left_layout)
        horizontal_layout.addLayout(mid_layout)
        horizontal_layout.addLayout(right_layout)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.name_text)
        vertical_layout.addWidget(self.name_entry)
        vertical_layout.addLayout(horizontal_layout)

        self.window.setLayout(vertical_layout)

        confirm.clicked.connect(self.on_confirm)
        confirm_and_save.clicked.connect(self.on_confirm_and_save)

    def __raise_emoji_popup(self, point: QPoint, line_edit: QTextEdit):
        def append_emoji(emoji: Emoji):
            return line_edit.insertPlainText(emoji.emoji)

        self.window.setCursor(Qt.CursorShape.WaitCursor)
        if self.emoji_picker_popup is None:
            self.emoji_picker_popup = QEmojiPickerPopup()
        emoji_picker = self.emoji_picker_popup.emoji_picker()
        emoji_picker.picked.connect(append_emoji)
        emoji_picker.reset()
        self.emoji_picker_popup.move(point.x() - 500, point.y() - 500)
        self.emoji_picker_popup.exec()
        self.emoji_picker_popup.hideEvent = emoji_picker.picked.disconnect(append_emoji)
        self.window.setCursor(Qt.CursorShape.ArrowCursor)

    def _add_condition(self, condition: str):
        translated_condition = self._translated_conditions[condition]
        item = QListWidgetItem()
        item.setText(translated_condition)
        item.setData(Qt.ItemDataRole.UserRole, condition)
        self.listbox_conditions.add_item(item)

    def __on_add_condition(self):
        index = self.conditions_combobox.currentIndex()
        condition = self.conditions_combobox.itemData(index, Qt.ItemDataRole.UserRole)
        if condition not in self.listbox_conditions.get_items_userdata():
            self._add_condition(condition)

    def is_name_valid(self):
        return self.get_name() not in interactions.message_names()

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

    def on_confirm(self):
        if not self.is_name_valid():
            message_box = QMessageBox()
            message_box.setWindowTitle(
                translate("MessageWindow", "Name already exists")
            )
            message_box.setWindowIcon(QIcon("source/icons/window-icon.svg"))
            message_box.setText(
                translate(
                    "MessageWindow",
                    "You can't set a message with a name that already exists.",
                )
            )
            message_box.exec()
        elif self.__has_opposite_conditions():
            message_box = QMessageBox()
            message_box.setWindowTitle(
                translate("MessageWindow", "Opposite conditions")
            )
            message_box.setWindowIcon(QIcon("source/icons/window-icon.svg"))
            message_box.setText(
                translate(
                    "MessageWindow",
                    "You can't have opposite conditions, please remove them.",
                )
            )
            message_box.exec()
        else:
            self.window.accept()

    def on_confirm_and_save(self):
        self.on_confirm()
        self.app.on_save_action()

    def __has_opposite_conditions(self) -> bool:
        conditions = self.listbox_conditions.get_items_userdata()
        for condition in conditions:
            opposite_condition = (
                condition[4:] if condition.startswith("not ") else f"not {condition}"
            )
            if opposite_condition in conditions:
                return True
        return False

    def get_name(self):
        return self.name_entry.text()

    def __del_checked(self, check_state: int):
        author_checkbox = self.group_where_react.findChild(QCheckBox, "author")
        author_checkbox.setDisabled(check_state == Qt.CheckState.Checked)

    def __author_checked(self, check_state: int):
        del_checkbox = self.group_pin_or_del.findChild(QCheckBox, "delete")
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
        result = {"expected message": self.listbox_messages.get_items_text()}
        reply_list = self.listbox_replies.get_items_text()
        result["reply"] = list(map(lambda replies: replies.split("¨"), reply_list))
        reactions_list = self.listbox_reactions.get_items_text()
        result["reaction"] = list(
            map(lambda reactions: list(emojis.get(reactions)), reactions_list)
        )
        result["conditions"] = self.listbox_conditions.get_items_userdata()
        result["pin or del"] = self.group_pin_or_del.get_checked_name()
        result["kick or ban"] = self.group_kick_or_ban.get_checked_name()
        result["where reply"] = self.group_where_reply.get_checked_name()
        result["where reaction"] = self.group_where_react.get_checked_name()
        result["delay"] = self.delay.value()

        return result


class EditMessageWindow(MessageWindow):
    def __init__(self, app, name: str, data: dict):
        super().__init__(app)
        self.__name = name
        self.name_entry.setText(name)

        self.listbox_messages.add_items(data["expected message"])

        for reply in data["reply"]:
            self.listbox_replies.add_item("¨".join(reply))

        for reaction in data["reaction"]:
            self.listbox_reactions.add_item("".join(reaction))

        for condition in data["conditions"]:
            self._add_condition(condition)

        pin_or_del = self.group_pin_or_del.findChild(QCheckBox, data["pin or del"])
        if pin_or_del and data["pin or del"]:
            pin_or_del.setChecked(True)

        self.delay.setValue(data["delay"])

        kick_or_ban = self.group_kick_or_ban.findChild(QCheckBox, data["kick or ban"])
        if kick_or_ban and data["kick or ban"]:
            kick_or_ban.setChecked(True)

        where_reply = self.group_where_reply.findChild(QCheckBox, data["where reply"])
        if where_reply and data["where reply"]:
            where_reply.setChecked(True)

        where_reaction = self.group_where_react.findChild(
            QCheckBox, data["where reaction"]
        )
        if where_reaction and data["where reaction"]:
            where_reaction.setChecked(True)

    def is_name_valid(self) -> bool:
        if self.get_name() == self.__name:
            return True
        else:
            return super().is_name_valid()


class NewMessageWindow(MessageWindow):
    pass
