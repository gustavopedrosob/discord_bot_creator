import logging
import webbrowser
from threading import Thread

from PySide6.QtCore import QPoint, QCoreApplication
from PySide6.QtGui import QIcon, QAction, Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QListWidget,
    QLabel,
    QMenuBar,
    QMenu,
    QComboBox,
    QMessageBox,
    QListWidgetItem,
)

from bot import IntegratedBot
from core.config import instance as config
from core.messages import messages
from interfaces.classes.qpassword import QPassword
from interfaces.credits.credits import CreditsWindow
from interfaces.main.log_handler import LogHandler
from interfaces.newmessage.main import EditMessageWindow, NewMessageWindow

logger = logging.getLogger(__name__)


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bot Discord Easy Creator")
        self.setMinimumSize(800, 600)
        self.resize(1000, 800)
        self.setWindowIcon(QIcon("source/icons/window-icon.svg"))

        self.message_window = None
        self.credits_window = CreditsWindow()
        self.bot = None
        self.bot_thread = None

        log_handler = LogHandler(self)
        log_handler.setLevel(logging.INFO)
        logger.addHandler(log_handler)

        # Create the menu bar
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # Create menus
        file_menu = QMenu(QCoreApplication.translate("QMainWindow", "File"), self)
        config_menu = QMenu(QCoreApplication.translate("QMainWindow", "Config"), self)
        edit_menu = QMenu(QCoreApplication.translate("QMainWindow", "Edit"), self)
        help_menu = QMenu(QCoreApplication.translate("QMainWindow", "Help"), self)

        # Add menus to the menu bar
        self.menu_bar.addMenu(file_menu)
        self.menu_bar.addMenu(config_menu)
        self.menu_bar.addMenu(edit_menu)
        self.menu_bar.addMenu(help_menu)

        language_menu = QMenu(
            QCoreApplication.translate("QMainWindow", "Language"), self
        )
        config_menu.addMenu(language_menu)

        english_action = QAction(
            QCoreApplication.translate("QMainWindow", "English"), self
        )
        english_action.triggered.connect(lambda: self.set_language("en_us"))
        portuguese_action = QAction(
            QCoreApplication.translate("QMainWindow", "Portuguese"), self
        )
        portuguese_action.triggered.connect(lambda: self.set_language("pt_br"))
        language_menu.addAction(english_action)
        language_menu.addAction(portuguese_action)

        # Create actions
        exit_action = QAction(QCoreApplication.translate("QMainWindow", "Exit"), self)
        exit_action.triggered.connect(self.close)
        credits_action = QAction(
            QCoreApplication.translate("QMainWindow", "Credits"), self
        )
        credits_action.triggered.connect(self.credits_window.window.show)
        project_action = QAction(
            QCoreApplication.translate("QMainWindow", "Project"), self
        )
        project_action.triggered.connect(
            lambda: webbrowser.open(
                "https://github.com/gustavopedrosob/bot_discord_easy_creator"
            )
        )
        report_action = QAction(
            QCoreApplication.translate("QMainWindow", "Report bug"), self
        )
        report_action.triggered.connect(
            lambda: webbrowser.open(
                "https://github.com/gustavopedrosob/bot_discord_easy_creator/issues/new"
            )
        )
        discord_applications = QAction(
            QCoreApplication.translate("QMainWindow", "Discord applications"), self
        )
        discord_applications.triggered.connect(
            lambda: webbrowser.open("https://discord.com/developers/applications/")
        )
        self.new_message_action = QAction(
            QCoreApplication.translate("QMainWindow", "New message"), self
        )
        self.new_message_action.triggered.connect(self.new_message)
        self.new_message_action.setShortcut("Ctrl+N")
        self.edit_message_action = QAction(
            QCoreApplication.translate("QMainWindow", "Edit message"), self
        )
        self.edit_message_action.triggered.connect(self.edit_selected_message)
        self.edit_message_action.setShortcut("Ctrl+E")
        self.remove_selected_message_action = QAction(
            QCoreApplication.translate("QMainWindow", "Remove message"), self
        )
        self.remove_selected_message_action.triggered.connect(
            self.confirm_remove_selected_message
        )
        self.remove_selected_message_action.setShortcut("Delete")
        self.remove_all_message_action = QAction(
            QCoreApplication.translate("QMainWindow", "Remove all messages"), self
        )
        self.remove_all_message_action.triggered.connect(self.confirm_remove_messages)
        self.remove_all_message_action.setShortcut("Ctrl+Delete")

        for action in [
            self.new_message_action,
            self.edit_message_action,
            self.remove_selected_message_action,
            self.remove_all_message_action,
        ]:
            self.addAction(action)

        # Add actions to the menus
        file_menu.addAction(exit_action)

        for action in [
            discord_applications,
            credits_action,
            project_action,
            report_action,
        ]:
            help_menu.addAction(action)

        edit_menu.addAction(self.new_message_action)
        edit_menu.addAction(self.remove_all_message_action)

        # Central Widget and Layouts
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Right Frame for Bot Controls
        right_frame = QVBoxLayout()
        self.logs_text_edit = QTextEdit()
        self.logs_text_edit.setPlaceholderText(
            QCoreApplication.translate("QMainWindow", "No logs at moment")
        )
        self.logs_text_edit.setReadOnly(True)

        # Command Entry Frame
        self.cmd_combobox = QComboBox()
        self.cmd_combobox.addItems(["clear"])
        self.cmd_combobox.setEditable(True)
        self.cmd_combobox.lineEdit().clear()
        self.cmd_combobox.lineEdit().setPlaceholderText("Cmd")
        self.cmd_combobox.lineEdit().returnPressed.connect(self.entry_command)

        # Token Entry Frame
        self.token_widget = QPassword()
        self.token_widget.line_edit.setText(config.get("token"))
        self.token_widget.line_edit.returnPressed.connect(self.update_token)

        # Execute Bot Button
        self.switch_bot_button = QPushButton(
            QCoreApplication.translate("QMainWindow", "Turn on bot")
        )
        self.switch_bot_button.clicked.connect(self.start_turn_on_bot_thread)

        # Adding Widgets to Right Frame
        right_frame.addWidget(self.logs_text_edit)
        right_frame.addWidget(self.cmd_combobox)
        right_frame.addWidget(QLabel("Token:"))
        right_frame.addWidget(self.token_widget)
        right_frame.addWidget(self.switch_bot_button)

        # Left Frame for Messages
        left_frame = QVBoxLayout()

        message_label = QLabel(QCoreApplication.translate("QMainWindow", "Messages"))

        self.messages_list_widget = QListWidget()
        self.messages_list_widget.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.messages_list_widget.customContextMenuRequested.connect(
            self.message_context_menu_event
        )

        new_message_button = QPushButton(
            QCoreApplication.translate("QMainWindow", "New")
        )
        new_message_button.clicked.connect(self.new_message)

        edit_messages_button = QPushButton(
            QCoreApplication.translate("QMainWindow", "Edit")
        )
        edit_messages_button.clicked.connect(self.edit_selected_message)

        remove_message_button = QPushButton(
            QCoreApplication.translate("QMainWindow", "Remove")
        )
        remove_message_button.clicked.connect(self.confirm_remove_selected_message)

        remove_all_message_button = QPushButton(
            QCoreApplication.translate("QMainWindow", "Remove all")
        )
        remove_all_message_button.clicked.connect(self.confirm_remove_messages)

        # Adding Widgets to Left Frame
        left_frame.addWidget(message_label)
        left_frame.addWidget(self.messages_list_widget)
        left_frame.addWidget(new_message_button)
        left_frame.addWidget(edit_messages_button)
        left_frame.addWidget(remove_message_button)
        left_frame.addWidget(remove_all_message_button)

        left_frame.setContentsMargins(0, 0, 10, 0)
        right_frame.setContentsMargins(10, 0, 0, 0)

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

    def set_language(self, language: str):
        warning = QMessageBox(self)
        warning.setWindowTitle(QCoreApplication.translate("QMainWindow", "Warning"))
        warning.setText(
            QCoreApplication.translate(
                "QMainWindow",
                "You need to restart the application to apply the changes.",
            )
        )
        warning.exec()
        config.set("language", language)
        config.save()

    @staticmethod
    def get_token():
        """Returns the current token saved in the "config.json" file."""
        return config.get("token")

    def __turn_on_bot(self):
        self.bot = IntegratedBot(self)
        self.bot.run(config.get("token"))

    def start_turn_on_bot_thread(self):
        self.bot_thread = Thread(target=self.__turn_on_bot)
        self.bot_thread.start()

    def entry_command(self):
        """Handles commands for the bot's log entry."""
        cmd = self.cmd_combobox.lineEdit().text()
        if cmd in ["cls", "clear"]:
            self.logs_text_edit.clear()
            self.cmd_combobox.clear()

    def update_token(self):
        """Updates the token in the "config.json" file and in the interface."""
        token = self.token_widget.line_edit.text()
        config.set("token", token)
        config.save()
        logger.info("Token salvo com sucesso!")

    def edit_selected_message(self):
        """Opens the NewMessage interface and loads saved information."""
        if self.__is_selecting_message():
            selected_message = self.__get_selected_message_text()
            self.message_window = EditMessageWindow(
                self, selected_message, messages.get(selected_message)
            )
            self.message_window.window.accepted.connect(
                lambda: self.accepted_edit_selected_message(
                    selected_message,
                    self.message_window.get_name(),
                    self.message_window.get_data(),
                )
            )
            self.message_window.window.exec()

    def accepted_edit_selected_message(
        self, old_message_name: str, new_message_name: str, message_data: dict
    ):
        if not new_message_name:
            new_message_name = old_message_name
        messages.delete(old_message_name)
        messages.set(new_message_name, message_data)
        messages.save()
        self.__get_list_item_message(old_message_name).setText(new_message_name)

    def accepted_new_message(self, message_name: str, message_data: dict):
        if not message_name:
            message_name = messages.new_id()
        messages.set(message_name, message_data)
        messages.save()
        self.messages_list_widget.addItem(message_name)

    def __get_selected_message(self) -> int:
        return self.messages_list_widget.selectedIndexes()[0].row()

    def __get_list_item_message(self, message: str) -> QListWidgetItem:
        return self.messages_list_widget.item(
            next(
                filter(
                    lambda i: self.messages_list_widget.item(i).text() == message,
                    range(self.messages_list_widget.count()),
                )
            )
        )

    def __get_selected_message_text(self) -> str:
        return self.messages_list_widget.selectedItems()[0].text()

    def __is_selecting_message(self) -> bool:
        return bool(self.messages_list_widget.selectedIndexes())

    def remove_selected_message(self):
        """Removes the selected message from the messages list and deletes it from "message and reply.json"."""
        selected_row = self.__get_selected_message()
        selected_message = self.__get_selected_message_text()
        self.messages_list_widget.takeItem(selected_row)
        messages.delete(selected_message)
        messages.save()

    def confirm_remove_selected_message(self):
        """Asks the user if they want to remove the selected message."""
        if self.__is_selecting_message():
            dialog = QMessageBox(self)
            dialog.setWindowTitle(
                QCoreApplication.translate("QMainWindow", "Remove message")
            )
            dialog.setText(
                QCoreApplication.translate(
                    "QMainWindow", "Are you sure you want to remove this message?"
                )
            )
            dialog.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            yes_button = dialog.button(QMessageBox.StandardButton.Yes)
            yes_button.setText(QCoreApplication.translate("QMainWindow", "Yes"))
            no_button = dialog.button(QMessageBox.StandardButton.No)
            no_button.setText(QCoreApplication.translate("QMainWindow", "No"))
            dialog.setDefaultButton(QMessageBox.StandardButton.No)
            dialog.accepted.connect(self.remove_selected_message)
            dialog.exec()

    def confirm_remove_messages(self):
        """Asks the user if they want to remove all messages."""
        dialog = QMessageBox(self)
        dialog.setWindowTitle(
            QCoreApplication.translate("QMainWindow", "Remove all messages")
        )
        dialog.setText(
            QCoreApplication.translate(
                "QMainWindow", "Are you sure you want to remove all messages?"
            )
        )
        dialog.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        yes_button = dialog.button(QMessageBox.StandardButton.Yes)
        yes_button.setText(QCoreApplication.translate("QMainWindow", "Yes"))
        no_button = dialog.button(QMessageBox.StandardButton.No)
        no_button.setText(QCoreApplication.translate("QMainWindow", "No"))
        dialog.setDefaultButton(QMessageBox.StandardButton.No)
        dialog.accepted.connect(self.remove_messages)
        dialog.exec()

    def remove_messages(self):
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
        self.switch_bot_button.setText(
            QCoreApplication.translate("QMainWindow", "Turn off bot")
        )
        self.switch_bot_button.clicked.disconnect(self.start_turn_on_bot_thread)
        self.switch_bot_button.clicked.connect(self.turn_off_bot)

    def turn_off_bot(self):
        self.bot.client.loop.create_task(self.bot.client.close())
        self.bot_thread.join()
        self.switch_bot_button.setText(
            QCoreApplication.translate("QMainWindow", "Turn on bot")
        )
        self.switch_bot_button.clicked.disconnect(self.turn_off_bot)
        self.switch_bot_button.clicked.connect(self.start_turn_on_bot_thread)
        logger.info("Bot desligado!")

    def message_context_menu_event(self, position: QPoint):
        context_menu = QMenu(self)
        context_menu.addAction(self.new_message_action)
        if self.__is_selecting_message():
            context_menu.addAction(self.edit_message_action)
            context_menu.addAction(self.remove_selected_message_action)
        context_menu.addAction(self.remove_all_message_action)
        context_menu.exec(self.messages_list_widget.mapToGlobal(position))
