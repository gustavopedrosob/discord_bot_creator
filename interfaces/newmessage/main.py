import typing

import emoji
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QIcon
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
)

from core.functions import have_in, raise_emoji_popup
from interfaces.newmessage.checkboxgroup import QCheckBoxGroup
from interfaces.newmessage.listbox import QListBox
from interpreter.conditions import conditions_keys


class MessageWindow:
    def __init__(self, app):
        self.app = app
        self.window = QDialog()
        self.window.setWindowFlags(
            self.window.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint
        )
        self.window.setWindowIcon(QIcon("source/icons/window-icon.svg"))
        self.window.setMinimumSize(800, 600)
        self.window.resize(800, 600)
        self.window.setWindowTitle(QCoreApplication.translate("QMainWindow", "Message"))

        left_layout = QVBoxLayout()
        mid_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        self.name_text = QLabel(QCoreApplication.translate("QMainWindow", "Name"))
        self.name_entry = QLineEdit()

        reactions_line_edit = QLineEdit()
        reactions_line_edit.mousePressEvent = lambda event: raise_emoji_popup()

        conditions_combobox = QComboBox()
        conditions_combobox.addItems(conditions_keys)

        self.listbox_conditions = QListBox(
            QCoreApplication.translate("QMainWindow", "Conditions"), conditions_combobox
        )
        self.listbox_reactions = QListBox(
            QCoreApplication.translate("QMainWindow", "Reactions"), reactions_line_edit
        )
        self.listbox_messages = QListBox(
            QCoreApplication.translate("QMainWindow", "Messages"), QLineEdit()
        )
        self.listbox_replies = QListBox(
            QCoreApplication.translate("QMainWindow", "Replies"), QLineEdit()
        )

        for widget in (
            self.listbox_conditions,
            self.listbox_reactions,
            self.listbox_messages,
            self.listbox_replies,
        ):
            left_layout.addWidget(widget)

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

    def on_save_and_quit(self):
        if self.__has_opposite_conditions():
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
            return
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

    def get_data(self):
        result = {}

        expected_message_list = self.listbox_messages.get_items_text()
        result["expected message"] = (
            expected_message_list if not len(expected_message_list) == 0 else None
        )

        reply_list = self.listbox_replies.get_items_text()
        result["reply"] = (
            list(map(lambda replies: replies.split("¨"), reply_list))
            if have_in(reply_list, "¨", reverse=True)
            else reply_list if not len(reply_list) == 0 else None
        )

        reactions_list = self.listbox_reactions.get_items_text()
        result["reaction"] = (
            list(
                map(
                    lambda reactions: [
                        emoji.demojize(reaction) for reaction in reactions
                    ],
                    reactions_list,
                )
            )
            if not len(reactions_list) == 0
            else None
        )

        conditions_list = self.listbox_conditions.get_items_text()
        result["conditions"] = (
            conditions_list if not len(conditions_list) == 0 else None
        )

        pin_or_del = self.group_pin_or_del.get_current_name()
        if pin_or_del:
            result["pin or del"] = pin_or_del

        kick_or_ban = self.group_kick_or_ban.get_current_name()
        if kick_or_ban:
            result["kick or ban"] = kick_or_ban

        selected_where_reply = self.group_where_reply.get_current_name()
        if selected_where_reply:
            result["where reply"] = selected_where_reply

        selected_where_react = self.group_where_react.get_current_name()
        if selected_where_react:
            result["where reaction"] = selected_where_react

        result["delay"] = self.delay.value()

        return result


class EditMessageWindow(MessageWindow):
    def __init__(self, app, name: str, data: dict):
        super().__init__(app)
        self.name_entry.setText(name)
        self.name_entry.setEnabled(False)

        if "expected message" in data:
            expected_messages = data["expected message"]
            if expected_messages:
                self.listbox_messages.add_items(expected_messages)

        if "reply" in data:
            replies = data["reply"]
            if replies:
                for reply in replies:
                    (
                        self.listbox_replies.add_item("¨".join(reply))
                        if type(reply) == list
                        else self.listbox_replies.add_item(reply)
                    )

        if "reaction" in data:
            reactions = data["reaction"]
            if reactions:
                list(
                    map(
                        lambda reaction: self.listbox_reactions.add_item(
                            "".join(
                                map(
                                    lambda r: emoji.emojize(r, language="alias"),
                                    reaction,
                                )
                            )
                        ),
                        reactions,
                    )
                )

        if "conditions" in data:
            conditions = data["conditions"]
            if conditions:
                self.listbox_conditions.add_items(conditions)

        if "pin or del" in data:
            pin_or_del = data["pin or del"]
            if pin_or_del == "pin":
                self.group_pin_or_del.get_checkbox("pin").setChecked(True)
            elif pin_or_del == "delete":
                self.group_pin_or_del.get_checkbox("delete").setChecked(True)

        if "delay" in data:
            delay = int(data["delay"])
            self.delay.setValue(delay)

        if "kick or ban" in data:
            kick_or_ban = data["kick or ban"]
            if kick_or_ban == "kick":
                self.group_kick_or_ban.get_checkbox("kick").setChecked(True)
            elif kick_or_ban == "ban":
                self.group_kick_or_ban.get_checkbox("ban").setChecked(True)

        if "where reply" in data:
            where_reply = data["where reply"]
            if where_reply == "group":
                self.group_where_reply.get_checkbox("group").setChecked(True)
            else:
                self.group_where_reply.get_checkbox("private").setChecked(True)

        if "where reaction" in data:
            where_reaction = data["where reaction"]
            if where_reaction == "author":
                self.group_where_react.get_checkbox("author").setChecked(True)
            else:
                self.group_where_react.get_checkbox("bot").setChecked(True)


class NewMessageWindow(MessageWindow):
    pass
