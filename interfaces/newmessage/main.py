import re
import typing

import emoji
from PySide6.QtCore import Qt
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
)

from core.functions import have_in
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
        self.window.setWindowTitle("Mensagem")

        left_layout = QVBoxLayout()
        mid_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        self.name_text = QLabel("Nome:")
        self.name_entry = QLineEdit()

        reactions_combox = QComboBox()
        reactions_combox.addItems([v["en"] for v in emoji.EMOJI_DATA.values()])
        reactions_combox.setEditable(True)

        conditions_combobox = QComboBox()
        conditions_combobox.addItems(conditions_keys)
        conditions_combobox.setEditable(True)

        self.listbox_conditions = QListBox("Condições", conditions_combobox)
        self.listbox_reactions = QListBox("Reações", reactions_combox)
        self.listbox_messages = QListBox("Mensagens", QLineEdit())
        self.listbox_replies = QListBox("Respostas", QLineEdit())

        for widget in (
            self.listbox_conditions,
            self.listbox_reactions,
            self.listbox_messages,
            self.listbox_replies,
        ):
            left_layout.addWidget(widget)

        self.group_pin_or_del = QCheckBoxGroup(QLabel("Ação:"))
        self.group_pin_or_del.add_checkbox("pin", QCheckBox("Fixar"))
        self.group_pin_or_del.add_checkbox("delete", QCheckBox("Deletar"))
        right_layout.addWidget(self.group_pin_or_del)

        self.group_kick_or_ban = QCheckBoxGroup(QLabel("Penalidade:"))
        self.group_kick_or_ban.add_checkbox("kick", QCheckBox("Expulsar"))
        self.group_kick_or_ban.add_checkbox("ban", QCheckBox("Banir"))
        right_layout.addWidget(self.group_kick_or_ban)

        self.group_where_reply = QCheckBoxGroup(QLabel("Onde responder:"))
        self.group_where_reply.add_checkbox("group", QCheckBox("Grupo"))
        self.group_where_reply.add_checkbox("private", QCheckBox("Privado"))
        right_layout.addWidget(self.group_where_reply)

        self.group_where_react = QCheckBoxGroup(QLabel("Onde reagir:"))
        self.group_where_react.add_checkbox("author", QCheckBox("Autor"))
        self.group_where_react.add_checkbox("bot", QCheckBox("Bot"))
        right_layout.addWidget(self.group_where_react)

        delay_label = QLabel("Delay:")
        self.delay = QSpinBox()

        # Save and quit button
        save_and_quit_button = QPushButton("Salvar e sair")
        save_and_quit_button.setAutoDefault(False)
        save_and_quit_button.setDefault(False)

        for widget in (
            delay_label,
            self.delay,
        ):
            right_layout.addWidget(widget)

        right_layout.addStretch()

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(save_and_quit_button)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addLayout(left_layout)
        horizontal_layout.addLayout(mid_layout)
        horizontal_layout.addLayout(right_layout)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.name_text)
        vertical_layout.addWidget(self.name_entry)
        vertical_layout.addLayout(horizontal_layout)
        vertical_layout.addLayout(buttons_layout)

        self.window.setLayout(vertical_layout)

        save_and_quit_button.clicked.connect(self.on_save_and_quit)

    def on_save_and_quit(self):
        # Adicionar validação de campos
        self.window.accept()

    def get_name(self):
        return self.name_entry.text()

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
                    lambda reactions: re.findall(r":[a-zA-Z_0-9]+:", reactions),
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

        if self.group_pin_or_del.get_current_name() == "pin":
            result["pin"] = True
        elif self.group_pin_or_del.get_current_name() == "delete":
            result["delete"] = True

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
                self.listbox_messages.list.addItems(expected_messages)

        if "reply" in data:
            replies = data["reply"]
            if replies:
                for reply in replies:
                    (
                        self.listbox_replies.list.addItem("¨".join(reply))
                        if type(reply) == list
                        else self.listbox_replies.list.addItem(reply)
                    )

        if "reaction" in data:
            reaction = data["reaction"]
            if reaction:
                list(
                    map(
                        lambda x: self.listbox_reactions.list.addItem(" ".join(x)),
                        reaction,
                    )
                )
        if "conditions" in data:
            conditions = data["conditions"]
            if conditions:
                self.listbox_conditions.list.addItems(conditions)

        if "pin" in data:
            pin = data["pin"]
            if pin:
                self.group_pin_or_del.get_checkbox("pin").setChecked(True)

        if "delete" in data:
            delete = data["delete"]
            if delete:
                self.group_pin_or_del.get_checkbox("delete").setChecked(True)

        if "delay" in data:
            delay = int(data["delay"])
            self.delay.setValue(delay)

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
