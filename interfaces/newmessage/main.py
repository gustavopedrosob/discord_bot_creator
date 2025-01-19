import typing

from PySide6.QtCore import Qt, QCoreApplication, QPoint, QRegularExpression, QMimeData
from PySide6.QtGui import (
    QIcon,
    QMouseEvent,
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
    QPushButton,
    QListWidget,
    QSpinBox,
    QLineEdit,
    QCheckBox,
    QMessageBox,
    QTextEdit,
)

from core.messages import messages
from interfaces.classes.collapse_group import QCollapseGroup
from interfaces.classes.colorresponsivebutton import QColorResponsiveButton
from interfaces.classes.emoji_picker import QEmojiPickerPopup
from interfaces.classes.emoji_validator import QEmojiValidator
from interfaces.classes.resposive_text_edit import QResponsiveTextEdit
from interfaces.newmessage.checkboxgroup import QCheckBoxGroup
from interfaces.newmessage.listbox import QListBox
from interpreter.conditions import conditions_keys


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
            self.insertPlainText(text)

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
        self.window.setWindowTitle(QCoreApplication.translate("QMainWindow", "Message"))

        left_layout = QVBoxLayout()
        mid_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        self.name_text = QLabel(QCoreApplication.translate("QMainWindow", "Name"))
        self.name_entry = QLineEdit()
        name_entry_validator = QRegularExpressionValidator(
            QRegularExpression(r"[\w ]*")
        )
        self.name_entry.setMaxLength(40)
        self.name_entry.setValidator(name_entry_validator)

        conditions_combobox = QComboBox()
        conditions_combobox.addItems(conditions_keys)
        self.listbox_conditions = QListBox(conditions_combobox)
        collapse_conditions = QCollapseGroup(
            QCoreApplication.translate("QMainWindow", "Conditions"),
            self.listbox_conditions,
        )
        collapse_conditions.setContentsMargins(0, 0, 0, 0)

        emoji_validator = QEmojiValidator()
        reactions_line_edit = QMessageTextEdit()
        reactions_line_edit.set_validator(emoji_validator)
        self.listbox_reactions = QListBox(reactions_line_edit)
        self.__add_emoji_button(
            self.listbox_reactions.entry_layout(), reactions_line_edit
        )
        collapse_reactions = QCollapseGroup(
            QCoreApplication.translate("QMainWindow", "Reactions"),
            self.listbox_reactions,
        )
        collapse_reactions.setContentsMargins(0, 0, 0, 0)

        messages_line_edit = QMessageTextEdit()
        # messages_line_edit.setMaxLength(2000)
        self.listbox_messages = QListBox(messages_line_edit)
        self.__add_emoji_button(
            self.listbox_messages.entry_layout(), messages_line_edit
        )
        collapse_messages = QCollapseGroup(
            QCoreApplication.translate("QMainWindow", "Messages"), self.listbox_messages
        )
        collapse_messages.setContentsMargins(0, 0, 0, 0)

        replies_line_edit = QMessageTextEdit()
        # replies_line_edit.setMaxLength(2000)
        self.listbox_replies = QListBox(replies_line_edit)
        self.__add_emoji_button(self.listbox_replies.entry_layout(), replies_line_edit)
        collapse_replies = QCollapseGroup(
            QCoreApplication.translate("QMainWindow", "Replies"), self.listbox_replies
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

        self.group_pin_or_del = QCheckBoxGroup(
            QLabel(QCoreApplication.translate("QMainWindow", "Action"))
        )
        self.group_pin_or_del.add_checkbox(
            "pin", QCheckBox(QCoreApplication.translate("QMainWindow", "Pin"))
        )
        del_checkbox = QCheckBox(QCoreApplication.translate("QMainWindow", "Delete"))
        del_checkbox.checkStateChanged.connect(self.__del_checked)
        self.group_pin_or_del.add_checkbox("delete", del_checkbox)
        right_layout.addWidget(self.group_pin_or_del)

        self.group_kick_or_ban = QCheckBoxGroup(
            QLabel(QCoreApplication.translate("QMainWindow", "Penalty"))
        )
        self.group_kick_or_ban.add_checkbox(
            "kick", QCheckBox(QCoreApplication.translate("QMainWindow", "Kick"))
        )
        self.group_kick_or_ban.add_checkbox(
            "ban", QCheckBox(QCoreApplication.translate("QMainWindow", "Ban"))
        )
        right_layout.addWidget(self.group_kick_or_ban)

        self.group_where_reply = QCheckBoxGroup(
            QLabel(QCoreApplication.translate("QMainWindow", "Where reply"))
        )
        self.group_where_reply.add_checkbox(
            "group", QCheckBox(QCoreApplication.translate("QMainWindow", "Group"))
        )
        self.group_where_reply.add_checkbox(
            "private", QCheckBox(QCoreApplication.translate("QMainWindow", "Private"))
        )
        right_layout.addWidget(self.group_where_reply)

        self.group_where_react = QCheckBoxGroup(
            QLabel(QCoreApplication.translate("QMainWindow", "Where react"))
        )
        author_checkbox = QCheckBox(QCoreApplication.translate("QMainWindow", "Author"))
        author_checkbox.checkStateChanged.connect(self.__author_checked)
        self.group_where_react.add_checkbox("author", author_checkbox)
        self.group_where_react.add_checkbox(
            "bot", QCheckBox(QCoreApplication.translate("QMainWindow", "Bot"))
        )
        right_layout.addWidget(self.group_where_react)

        delay_label = QLabel(QCoreApplication.translate("QMainWindow", "Delay"))
        self.delay = QSpinBox()

        # Save and quit button
        save_and_quit_button = QPushButton(
            QCoreApplication.translate("QMainWindow", "Save and quit")
        )
        save_and_quit_button.setAutoDefault(False)
        save_and_quit_button.setDefault(False)

        for widget in (
            delay_label,
            self.delay,
        ):
            right_layout.addWidget(widget)

        right_layout.addStretch()
        right_layout.addWidget(save_and_quit_button)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addLayout(left_layout)
        horizontal_layout.addLayout(mid_layout)
        horizontal_layout.addLayout(right_layout)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.name_text)
        vertical_layout.addWidget(self.name_entry)
        vertical_layout.addLayout(horizontal_layout)

        self.window.setLayout(vertical_layout)

        save_and_quit_button.clicked.connect(self.on_save_and_quit)

    @staticmethod
    def __raise_emote_popup(point: QPoint, line_edit: QTextEdit):
        emoji_picker_popup = QEmojiPickerPopup()
        emoji_picker = emoji_picker_popup.emoji_picker()
        emoji_picker.emoji_click.connect(
            lambda text: line_edit.setPlainText(line_edit.toPlainText() + text)
        )
        emoji_picker_popup.move(point.x() - 500, point.y() - 500)
        emoji_picker_popup.exec()

    def is_name_valid(self):
        return self.get_name() not in messages.message_names()

    def __add_emoji_button(
        self, layout: QHBoxLayout, line_edit: typing.Union[QLineEdit, QTextEdit]
    ):
        emote_button = QColorResponsiveButton()
        emote_button.setIcon(QIcon("source/icons/face-smile-solid.svg"))
        emote_button.setFlat(True)
        layout.addWidget(emote_button, alignment=Qt.AlignmentFlag.AlignTop)
        emote_button.clicked.connect(
            lambda: self.__raise_emote_popup(
                emote_button.mapToGlobal(QPoint(0, 0)), line_edit
            )
        )

    def on_save_and_quit(self):
        if not self.is_name_valid():
            message_box = QMessageBox()
            message_box.setWindowTitle(
                QCoreApplication.translate("QMainWindow", "Name already exists")
            )
            message_box.setWindowIcon(QIcon("source/icons/window-icon.svg"))
            message_box.setText(
                QCoreApplication.translate(
                    "QMainWindow",
                    "You can't set a message with a name that already exists.",
                )
            )
            message_box.exec()
        elif self.__has_opposite_conditions():
            message_box = QMessageBox()
            message_box.setWindowTitle(
                QCoreApplication.translate("QMainWindow", "Opposite conditions")
            )
            message_box.setWindowIcon(QIcon("source/icons/window-icon.svg"))
            message_box.setText(
                QCoreApplication.translate(
                    "QMainWindow",
                    "You can't have opposite conditions, please remove them.",
                )
            )
            message_box.exec()
        else:
            self.window.accept()

    def __has_opposite_conditions(self) -> bool:
        conditions = self.listbox_conditions.get_items_text()
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
        author_checkbox = self.group_where_react.get_checkbox("author")
        if check_state == Qt.CheckState.Checked:
            author_checkbox.setDisabled(True)
        else:
            author_checkbox.setDisabled(False)

    def __author_checked(self, check_state: int):
        del_checkbox = self.group_pin_or_del.get_checkbox("delete")
        if check_state == Qt.CheckState.Checked:
            del_checkbox.setDisabled(True)
        else:
            del_checkbox.setDisabled(False)

    @staticmethod
    def insert_on_listbox(
        listbox: QListWidget, entry: typing.Union[QLineEdit, QComboBox], limit: int = 0
    ):
        """insere um valor na listbox especificada e apaga o conteúdo da entry especificada,
        se um limite for especificado ele vai checar se o limite da listbox não foi atingido
        """
        value = entry.text() if isinstance(entry, QLineEdit) else entry.currentText()
        if value:
            listbox_length = listbox.count()
            if not listbox_length > limit or limit == 0:
                listbox.addItem(value)
                entry.clear()

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
            map(lambda reactions: list(reactions), reactions_list)
        )
        result["conditions"] = self.listbox_conditions.get_items_text()
        result["pin or del"] = self.group_pin_or_del.get_current_name()
        result["kick or ban"] = self.group_kick_or_ban.get_current_name()
        result["where reply"] = self.group_where_reply.get_current_name()
        result["where reaction"] = self.group_where_react.get_current_name()
        result["delay"] = self.delay.value()

        return result


class EditMessageWindow(MessageWindow):
    def __init__(self, app, name: str, data: dict):
        super().__init__(app)
        self.__name = name
        self.name_entry.setText(name)

        expected_messages = data["expected message"]
        if expected_messages:
            self.listbox_messages.add_items(expected_messages)

        replies = data["reply"]
        if replies:
            for reply in replies:
                (self.listbox_replies.add_item("¨".join(reply)))

        reactions_list = data["reaction"]
        if reactions_list:
            list(
                map(
                    lambda reactions: self.listbox_reactions.add_item(
                        "".join(reactions)
                    ),
                    reactions_list,
                )
            )

        self.listbox_conditions.add_items(data["conditions"])

        pin_or_del = self.group_pin_or_del.get_checkbox(data["pin or del"])
        if pin_or_del:
            pin_or_del.setChecked(True)

        self.delay.setValue(data["delay"])

        kick_or_ban = self.group_kick_or_ban.get_checkbox(data["kick or ban"])
        if kick_or_ban:
            kick_or_ban.setChecked(True)

        where_reply = self.group_where_reply.get_checkbox(data["where reply"])
        if where_reply:
            where_reply.setChecked(True)

        where_reaction = self.group_where_react.get_checkbox(data["where reaction"])
        if where_reaction:
            where_reaction.setChecked(True)

    def is_name_valid(self) -> bool:
        if self.get_name() == self.__name:
            return True
        else:
            return super().is_name_valid()


class NewMessageWindow(MessageWindow):
    pass
