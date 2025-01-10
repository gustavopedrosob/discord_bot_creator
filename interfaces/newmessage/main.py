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
    QFrame,
    QComboBox,
    QPushButton,
    QListWidget,
    QSpinBox,
    QLineEdit,
    QCheckBox,
)

from core.functions import have_in
from interfaces.newmessage.radiogroup import QRadioGroup
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

        # Widgets
        self.name_text = QLabel("Nome:")
        self.name_entry = QLineEdit()

        expected_message_text = QLabel("Mensagem esperada")
        self.expected_message = QLineEdit()

        reply_text = QLabel("Resposta")
        self.reply = QLineEdit()

        reactions_text = QLabel("Reações")
        self.reactions = QComboBox()
        self.reactions.addItems([""] + [v["en"] for v in emoji.EMOJI_DATA.values()])

        conditions_text = QLabel("Condições")
        self.conditions = QComboBox()
        self.conditions.addItems([""] + conditions_keys)

        add_button = QPushButton("Adicionar")

        # Layout setup
        for widget in [
            expected_message_text,
            self.expected_message,
            reply_text,
            self.reply,
            reactions_text,
            self.reactions,
            conditions_text,
            self.conditions,
        ]:
            left_layout.addWidget(widget)

        left_layout.addStretch()

        # Listboxes setup
        listbox_frame = QFrame(self.window)

        listbox_conditions_text = QLabel("Condições", listbox_frame)
        self.listbox_conditions = QListWidget(listbox_frame)

        listbox_reactions_text = QLabel("Reações", listbox_frame)
        self.listbox_reactions = QListWidget(listbox_frame)

        listbox_messages_text = QLabel("Mensagens", listbox_frame)
        self.listbox_messages = QListWidget(listbox_frame)

        listbox_replies_text = QLabel("Respostas", listbox_frame)
        self.listbox_replies = QListWidget(listbox_frame)

        remove_button = QPushButton("Remover", listbox_frame)
        remove_all_button = QPushButton("Remover todos", listbox_frame)

        # Adding widgets to layout
        for widget in [
            listbox_conditions_text,
            self.listbox_conditions,
            listbox_replies_text,
            self.listbox_replies,
            listbox_messages_text,
            self.listbox_messages,
            listbox_reactions_text,
            self.listbox_reactions,
        ]:
            mid_layout.addWidget(widget)

        frame_options = QFrame(self.window)

        self.group_pin_or_del = QRadioGroup(QLabel("Ação"))
        self.group_pin_or_del.add_radio("pin", QCheckBox("Fixar"))
        self.group_pin_or_del.add_radio("delete", QCheckBox("Deletar"))
        right_layout.addLayout(self.group_pin_or_del.layout)

        self.group_kick_or_ban = QRadioGroup(QLabel("Penalidade"))
        self.group_kick_or_ban.add_radio("kick", QCheckBox("Expulsar"))
        self.group_kick_or_ban.add_radio("ban", QCheckBox("Banir"))
        right_layout.addLayout(self.group_kick_or_ban.layout)

        self.group_where_reply = QRadioGroup(QLabel("Onde responder"))
        self.group_where_reply.add_radio("group", QCheckBox("Grupo"))
        self.group_where_reply.add_radio("private", QCheckBox("Privado"))
        right_layout.addLayout(self.group_where_reply.layout)

        self.group_where_react = QRadioGroup(QLabel("Onde reagir"))
        self.group_where_react.add_radio("author", QCheckBox("Autor"))
        self.group_where_react.add_radio("bot", QCheckBox("Bot"))
        right_layout.addLayout(self.group_where_react.layout)

        delay_label = QLabel("Delay:")
        self.delay = QSpinBox()
        self.delay.setFixedWidth(250)

        # Save and quit button
        save_and_quit_button = QPushButton("Salvar e sair", frame_options)

        for widget in (
            delay_label,
            self.delay,
        ):
            right_layout.addWidget(widget)

        right_layout.addStretch()

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(remove_button)
        buttons_layout.addWidget(remove_all_button)
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

        remove_button.clicked.connect(self.remove_all_selected_on_listbox)
        remove_all_button.clicked.connect(self.remove_all_on_listbox)
        save_and_quit_button.clicked.connect(self.on_save_and_quit)
        add_button.clicked.connect(self.insert_any_on_listbox)

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

    def insert_any_on_listbox(self):
        for listbox, entry in zip(self.__all_listbox(), self.__all_entries()):
            # se for o reactions, no discord o limite de reações por mensagem é de 20,
            # ou seja, a gente precisa limitar a quantidade de reactions.
            self.insert_on_listbox(
                listbox, entry, limit=19 if entry == self.reactions else 0
            )

    @staticmethod
    def remove_selected_on_listbox(listbox: QListWidget):
        """remove um item selecionado na listbox"""
        for item in listbox.selectedItems():
            listbox.takeItem(listbox.indexFromItem(item).row())

    def remove_all_selected_on_listbox(self):
        for listbox in self.__all_listbox():
            self.remove_selected_on_listbox(listbox)

    def remove_all_on_listbox(self):
        """remove todos os items em todas listbox"""
        for listbox in self.__all_listbox():
            listbox: QListWidget
            listbox.clear()

    def __all_listbox(self):
        return (
            self.listbox_messages,
            self.listbox_replies,
            self.listbox_reactions,
            self.listbox_conditions,
        )

    def __all_entries(self):
        return self.expected_message, self.reply, self.reactions, self.conditions

    def get_data(self):
        result = {}

        expected_message_list = [
            self.listbox_messages.item(i).text()
            for i in range(self.listbox_messages.count())
        ]
        result["expected message"] = (
            expected_message_list if not len(expected_message_list) == 0 else None
        )

        reply_list = [
            self.listbox_replies.item(i).text()
            for i in range(self.listbox_replies.count())
        ]
        result["reply"] = (
            list(map(lambda replies: replies.split("¨"), reply_list))
            if have_in(reply_list, "¨", reverse=True)
            else reply_list if not len(reply_list) == 0 else None
        )

        reactions_list = [
            self.listbox_reactions.item(i).text()
            for i in range(self.listbox_reactions.count())
        ]
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

        conditions_list = [
            self.listbox_conditions.item(i).text()
            for i in range(self.listbox_conditions.count())
        ]
        result["conditions"] = (
            conditions_list if not len(conditions_list) == 0 else None
        )

        if self.group_pin_or_del.current_name == "pin":
            result["pin"] = True
        elif self.group_pin_or_del.current_name == "delete":
            result["delete"] = True

        selected_where_reply = self.group_where_reply.current_name
        if selected_where_reply:
            result["where reply"] = selected_where_reply.objectName()

        selected_where_react = self.group_where_react.current_name
        if selected_where_react:
            result["where reaction"] = selected_where_react.objectName()

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
                for expected_message in expected_messages:
                    self.listbox_messages.addItem(expected_message)

        if "reply" in data:
            replies = data["reply"]
            if replies:
                for reply in replies:
                    (
                        self.listbox_replies.addItem("¨".join(reply))
                        if type(reply) == list
                        else self.listbox_replies.addItem(reply)
                    )

        if "reaction" in data:
            reaction = data["reaction"]
            if reaction:
                list(
                    map(
                        lambda x: self.listbox_reactions.addItem(" ".join(x)),
                        reaction,
                    )
                )
        if "conditions" in data:
            conditions = data["conditions"]
            if conditions:
                for condition in conditions:
                    self.listbox_conditions.addItem(condition)

        if "pin" in data:
            pin = data["pin"]
            if pin:
                self.group_pin_or_del.radios["pin"].setChecked(True)

        if "delete" in data:
            delete = data["delete"]
            if delete:
                self.group_pin_or_del.radios["delete"].setChecked(True)

        if "delay" in data:
            delay = int(data["delay"])
            self.delay.setValue(delay)

        if "where reply" in data:
            where_reply = data["where reply"]
            if where_reply == "group":
                self.group_where_reply.radios["group"].setChecked(True)
            else:
                self.group_where_reply.radios["private"].setChecked(True)

        if "where reaction" in data:
            where_reaction = data["where reaction"]
            if where_reaction == "author":
                self.group_where_react.radios["author"].setChecked(True)
            else:
                self.group_where_react.radios["bot"].setChecked(True)


class NewMessageWindow(MessageWindow):
    pass
