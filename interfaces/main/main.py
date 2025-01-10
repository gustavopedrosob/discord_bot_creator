import logging
import typing
from threading import Thread

from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QListWidget,
    QLabel,
    QMenuBar,
    QMenu,
)

from bot import IntegratedBot
from core.config import instance as config
from core.messages import messages
from interfaces.classes.qpassword import QPassword
from interfaces.credits.credits import CreditsWindow
from interfaces.newmessage.main import EditMessageWindow, NewMessageWindow

logger = logging.getLogger(__name__)


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bot Discord Easy Creator")
        self.setMinimumSize(800, 600)
        self.setWindowIcon(QIcon("source/icons/window-icon.svg"))

        self.message_window = None
        self.credits_window = CreditsWindow()
        self.bot = None
        self.bot_thread = None

        # Create the menu bar
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # Create menus
        file_menu = QMenu("&Arquivo", self)
        edit_menu = QMenu("&Editar", self)
        help_menu = QMenu("&Ajuda", self)

        # Add menus to the menu bar
        self.menu_bar.addMenu(file_menu)
        self.menu_bar.addMenu(edit_menu)
        self.menu_bar.addMenu(help_menu)

        # Create actions
        exit_action = QAction("&Sair", self)
        exit_action.triggered.connect(self.close)
        credits_action = QAction("&Creditos", self)
        credits_action.triggered.connect(self.credits_window.window.show)
        add_message_action = QAction("&Adicionar mensagem", self)
        add_message_action.triggered.connect(self.new_message)
        remove_all_message_action = QAction("&Apagar todas mensagens", self)
        remove_all_message_action.triggered.connect(self.clear_messages)

        # Add actions to the menus
        file_menu.addAction(exit_action)
        help_menu.addAction(credits_action)
        edit_menu.addAction(add_message_action)
        edit_menu.addAction(remove_all_message_action)

        # Central Widget and Layouts
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Right Frame for Bot Controls
        right_frame = QVBoxLayout()
        self.logs_text_edit = QTextEdit()
        self.logs_text_edit.setPlaceholderText("No momento não há logs.")
        self.logs_text_edit.setReadOnly(True)

        # Command Entry Frame
        self.cmd_line_edit = QLineEdit()
        self.cmd_line_edit.setPlaceholderText("Cmd")
        self.cmd_line_edit.returnPressed.connect(self.entry_command)

        # Token Entry Frame
        self.token_widget = QPassword()
        self.token_widget.line_edit.setText(config.get("token"))
        self.token_widget.line_edit.returnPressed.connect(self.update_token)

        # Execute Bot Button
        self.exec_bot_button = QPushButton("Executar o bot")
        self.exec_bot_button.clicked.connect(self.init_bot)

        # Adding Widgets to Right Frame
        right_frame.addWidget(self.logs_text_edit)
        right_frame.addWidget(self.cmd_line_edit)
        right_frame.addWidget(QLabel("Token:"))
        right_frame.addWidget(self.token_widget)
        right_frame.addWidget(self.exec_bot_button)

        # Left Frame for Messages
        left_frame = QVBoxLayout()

        edit_messages_button = QPushButton("Editar mensagem")
        edit_messages_button.clicked.connect(self.edit_selected_message)

        self.messages_list_widget = QListWidget()

        add_message_button = QPushButton("Adicionar mensagem")
        add_message_button.clicked.connect(self.new_message)

        remove_message_button = QPushButton("Apagar mensagem")
        remove_message_button.clicked.connect(self.remove_selected_message)

        remove_all_message_button = QPushButton("Apagar todas mensagens")
        remove_all_message_button.clicked.connect(self.clear_messages)

        # Adding Widgets to Left Frame
        left_frame.addWidget(self.messages_list_widget)
        left_frame.addWidget(add_message_button)
        left_frame.addWidget(edit_messages_button)
        left_frame.addWidget(remove_message_button)
        left_frame.addWidget(remove_all_message_button)

        main_layout.addLayout(left_frame)
        main_layout.addLayout(right_frame)

        main_layout.setStretch(1, 1)

        self.load_messages()

    def new_message(self):
        if self.message_window:
            self.message_window.window.reject()
        self.message_window = NewMessageWindow(self)
        self.message_window.window.accepted.connect(
            lambda: self.accepted_new_message(
                self.message_window.get_name(), self.message_window.get_data()
            )
        )
        self.message_window.window.exec()

    @staticmethod
    def get_token():
        """Returns the current token saved in the "config.json" file."""
        return config.get("token")

    def __run_bot(self):
        self.bot = IntegratedBot(self)
        self.bot.run()

    def init_bot(self):
        self.bot_thread = Thread(target=self.__run_bot)
        self.bot_thread.start()

    def entry_command(self):
        """Handles commands for the bot's log entry."""
        cmd = self.cmd_line_edit.text()
        if cmd in ["cls", "clear"]:
            self.logs_text_edit.clear()
            self.cmd_line_edit.clear()

    def update_token(self):
        """Updates the token in the "config.json" file and in the interface."""
        token = self.token_widget.line_edit.text()
        config.set("token", token)
        config.save()

    def edit_selected_message(self):
        """Opens the NewMessage interface and loads saved information."""
        try:
            _, selected_message = self.__get_selected_message()
        except IndexError:
            pass
        else:
            self.message_window = EditMessageWindow(
                self, selected_message, messages.get(selected_message)
            )
            self.message_window.window.accepted.connect(
                lambda: self.accepted_edit_selected_message(
                    selected_message, self.message_window.get_data()
                )
            )
            self.message_window.window.exec()

    @staticmethod
    def accepted_edit_selected_message(message_name: str, message_data: dict):
        messages.set(message_name, message_data)
        messages.save()

    def accepted_new_message(self, message_name: str, message_data: dict):
        if not message_name:
            message_name = messages.new_id()
        messages.set(message_name, message_data)
        messages.save()
        self.messages_list_widget.addItem(message_name)

    def __get_selected_message(self) -> typing.Tuple[int, str]:
        index = self.messages_list_widget.selectedIndexes()[0].row()
        return index, self.messages_list_widget.item(index).text()

    def remove_selected_message(self):
        """Removes the selected message from the messages list and deletes it from "message and reply.json"."""
        try:
            selected_row, selected_message = self.__get_selected_message()
        except IndexError:
            pass
        else:
            self.messages_list_widget.takeItem(selected_row)
            messages.delete(selected_message)
            messages.save()

    def clear_messages(self):
        """Removes all messages from the list."""
        self.messages_list_widget.clear()
        messages.clear()
        messages.save()

    def load_messages(self):
        """Loads all messages from "message and reply.json" and inserts them into the messages list."""
        messages.load()
        for message_name in messages.message_names():
            self.messages_list_widget.addItem(message_name)

    def log(self, message):
        self.logs_text_edit.insertPlainText(message)

    def change_init_bot_button(self):
        self.exec_bot_button.setText("Desligar o bot")
        self.exec_bot_button.clicked.disconnect(self.init_bot)
        self.exec_bot_button.clicked.connect(self.turnoff_bot)

    def turnoff_bot(self):
        self.bot.client.loop.create_task(self.bot.client.close())
        self.bot_thread.join()
        self.exec_bot_button.setText("Executar o bot")
        self.exec_bot_button.clicked.disconnect(self.turnoff_bot)
        self.exec_bot_button.clicked.connect(self.init_bot)
        logger.info("Bot desligado!")
