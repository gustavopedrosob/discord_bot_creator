import html
import logging
import os
import typing
from pathlib import Path

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QIcon, Qt, QCloseEvent, QTextCursor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLabel,
    QComboBox,
    QMessageBox,
    QListWidgetItem,
    QFileDialog,
    QMainWindow,
    QTabWidget,
)
from discord.abc import Messageable
from extra_qwidgets.utils import get_awesome_icon, colorize_icon
from extra_qwidgets.widgets.color_button import QColorButton
from extra_qwidgets.widgets.password import QPassword

from core.config import instance as config
from core.interactions import interactions, Interactions
from interfaces.classes.confirm_message_box import QConfirmMessageBox
from interfaces.classes.custom_button import QCustomButton
from interfaces.credits.credits import CreditsWindow
from interfaces.group.group import GroupWindow
from interfaces.main.bot_thread import QBotThread
from interfaces.main.groups_list import QGroupsList
from interfaces.main.log_handler import log_handler
from interfaces.main.menu_bar import MenuBar
from interfaces.main.messages_list import QMessagesList
from interfaces.messages.messages import EditMessageWindow, NewMessageWindow


logger = logging.getLogger(__name__)
logger.addHandler(log_handler)
translate = QCoreApplication.translate


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.resize(1000, 800)
        self.setWindowIcon(QIcon("source/icons/window-icon.svg"))

        self.group_window = None
        self.message_window = None
        self.credits_window = CreditsWindow()
        self.bot_thread = QBotThread()
        self.menu_bar = MenuBar(self)
        log_handler.set_signal(self.bot_thread.log)

        self.logs_text_edit = QTextEdit()
        self.logs_text_edit.setPlaceholderText(
            translate("MainWindow", "No logs at moment")
        )
        self.logs_text_edit.setReadOnly(True)
        self.logs_text_edit.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.cmd_combobox = QComboBox()
        self.cmd_combobox.addItems(["clear"])
        self.cmd_combobox.setEditable(True)
        self.cmd_combobox.lineEdit().clear()
        self.cmd_combobox.lineEdit().setPlaceholderText("Cmd")

        self.token_widget = QPassword()
        self.token_widget.line_edit.setText(config.get("token"))
        self.token_widget.line_edit.setMaxLength(100)

        self.turn_on_bot_button = QColorButton(
            translate("MainWindow", "Turn on bot"), "#3e92cc"
        )
        self.turn_on_bot_button.setIcon(
            colorize_icon(get_awesome_icon("play"), "#FFFFFF")
        )
        self.turn_off_bot_button = QColorButton(
            translate("MainWindow", "Turn off bot"), "#d8315b"
        )
        self.turn_off_bot_button.setIcon(
            colorize_icon(get_awesome_icon("stop"), "#FFFFFF")
        )
        self.update_bot_button()

        self.groups_list_widget = QGroupsList()
        self.config_group_button = QCustomButton(translate("MainWindow", "Config"))
        self.quit_group_button = QCustomButton(translate("MainWindow", "Quit"))
        self.messages_list_widget = QMessagesList()
        self.new_message_button = QCustomButton(translate("MainWindow", "New"))
        self.edit_messages_button = QCustomButton(translate("MainWindow", "Edit"))
        self.remove_message_button = QCustomButton(translate("MainWindow", "Remove"))
        self.remove_all_message_button = QCustomButton(
            translate("MainWindow", "Remove all")
        )

        file = Path(config.get("file"))

        if file.name == "":
            self.set_window_title()
        elif file.exists() and file.is_file():
            self.load_interactions(file)
            self.set_window_title(file)
        else:
            self.file_dont_exists_message_box()
            config.set("file", "")
            config.save()
            self.set_window_title()

        self.setup_binds()
        self.setup_layout()
        self.setup_menus()

    def setup_menus(self):
        self.setMenuBar(self.menu_bar)
        self.addActions(
            (
                self.messages_list_widget.new_action,
                self.messages_list_widget.edit_action,
                self.messages_list_widget.remove_action,
                self.messages_list_widget.remove_all_action,
            )
        )
        self.menu_bar.edit.addActions(
            (
                self.messages_list_widget.new_action,
                self.messages_list_widget.remove_all_action,
            )
        )

    def setup_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        right_frame = QVBoxLayout()
        for widget in [
            self.logs_text_edit,
            self.cmd_combobox,
            QLabel("Token:"),
            self.token_widget,
            self.turn_on_bot_button,
            self.turn_off_bot_button,
        ]:
            right_frame.addWidget(widget)
        groups_widget = QWidget()
        groups_widget.setContentsMargins(5, 5, 5, 5)
        groups_layout = QVBoxLayout()
        groups_widget.setLayout(groups_layout)
        groups_layout.addWidget(self.groups_list_widget)
        groups_layout.addWidget(self.config_group_button)
        groups_layout.addWidget(self.quit_group_button)
        messages_widget = QWidget()
        messages_widget.setContentsMargins(5, 5, 5, 5)
        messages_layout = QVBoxLayout()
        messages_widget.setLayout(messages_layout)
        left_widget = QTabWidget()
        left_widget.addTab(messages_widget, translate("MainWindow", "Messages"))
        left_widget.addTab(groups_widget, translate("MainWindow", "Groups"))
        for widget in [
            self.messages_list_widget,
            self.new_message_button,
            self.edit_messages_button,
            self.remove_message_button,
            self.remove_all_message_button,
        ]:
            messages_layout.addWidget(widget)
        left_widget.setContentsMargins(0, 0, 10, 0)
        right_frame.setContentsMargins(10, 0, 0, 0)
        main_layout.addWidget(left_widget)
        main_layout.addLayout(right_frame)
        main_layout.setStretch(1, 1)

    def setup_binds(self):
        self.new_message_button.clicked.connect(self.new_message)
        self.edit_messages_button.clicked.connect(self.edit_selected_message)
        self.remove_message_button.clicked.connect(self.confirm_remove_selected_message)
        self.remove_all_message_button.clicked.connect(self.confirm_remove_messages)
        self.turn_on_bot_button.clicked.connect(self.start_turn_on_bot_thread)
        self.turn_off_bot_button.clicked.connect(self.turn_off_bot)
        self.messages_list_widget.new_action.triggered.connect(self.new_message)
        self.messages_list_widget.edit_action.triggered.connect(
            self.edit_selected_message
        )
        self.messages_list_widget.remove_action.triggered.connect(
            self.confirm_remove_selected_message
        )
        self.messages_list_widget.remove_all_action.triggered.connect(
            self.confirm_remove_messages
        )
        self.menu_bar.help.credits.triggered.connect(self.credits_window.window.show)
        self.menu_bar.file.exit.triggered.connect(self.close)
        self.menu_bar.file.save_as.triggered.connect(self.on_save_as_action)
        self.menu_bar.file.save.triggered.connect(self.on_save_action)
        self.menu_bar.file.load.triggered.connect(self.on_load_action)
        self.menu_bar.file.new.triggered.connect(self.on_new_action)
        self.menu_bar.config.language.english.triggered.connect(
            lambda: self.set_language("en_us")
        )
        self.menu_bar.config.language.portuguese.triggered.connect(
            lambda: self.set_language("pt_br")
        )
        self.bot_thread.finished.connect(self.on_bot_thread_finished)
        self.bot_thread.bot_ready.connect(self.on_bot_ready)
        self.bot_thread.login_failure.connect(self.on_login_failure)
        self.bot_thread.log.connect(self.log)
        self.bot_thread.guild_join.connect(self.update_groups)
        self.bot_thread.guild_remove.connect(self.update_groups)
        self.bot_thread.guild_update.connect(self.update_groups)
        self.groups_list_widget.config_action.triggered.connect(
            self.config_selected_group
        )
        self.groups_list_widget.quit_action.triggered.connect(self.quit_selected_group)
        self.config_group_button.clicked.connect(self.config_selected_group)
        self.quit_group_button.clicked.connect(self.quit_selected_group)
        self.token_widget.line_edit.textEdited.connect(self.update_token)
        self.cmd_combobox.lineEdit().returnPressed.connect(self.entry_command)

    def config_selected_group(self):
        if self.__is_selecting_group():
            selected_group_id = self.__get_selected_group_user_data()
            groups = interactions.get("groups")
            group = self.bot_thread.groups()[selected_group_id]
            group_interaction = groups.get(str(selected_group_id))
            welcome_message_channel, welcome_message = None, None
            if group_interaction:
                channels = {
                    c.id: c for c in group.channels if isinstance(c, Messageable)
                }
                if group_interaction["welcome_message_channel"]:
                    welcome_message_channel = channels[
                        group_interaction["welcome_message_channel"]
                    ]
                welcome_message = group_interaction["welcome_message"]

            self.group_window = GroupWindow(
                self.__get_selected_group_text(),
                group.text_channels,
                group.voice_channels,
                welcome_message_channel,
                welcome_message,
            )
            self.group_window.accepted.connect(
                lambda: self.save_selected_group(selected_group_id)
            )
            self.group_window.exec()

    def save_selected_group(self, group_id: int):
        data = self.group_window.get_data()
        groups = interactions.get("groups")
        groups[str(group_id)] = data
        self.on_save_action()

    def quit_selected_group(self):
        if self.__is_selecting_group():
            selected_group = self.__get_selected_group()
            item = self.groups_list_widget.item(selected_group)
            group_id = item.data(Qt.ItemDataRole.UserRole)
            self.groups_list_widget.takeItem(selected_group)
            self.bot_thread.leave_group(group_id)

    def update_groups(self):
        self.groups_list_widget.clear()
        for group_id, group in self.bot_thread.groups().items():
            group = QListWidgetItem(group.name)
            group.setData(Qt.ItemDataRole.UserRole, group_id)
            self.groups_list_widget.addItem(group)

    def on_login_failure(self):
        self.warning_message_box(
            translate("MainWindow", "Login failure"),
            translate("MainWindow", "Improper token has been passed."),
        )
        self.turn_on_bot_button.setDisabled(False)

    def warning_message_box(self, title: str, text: str):
        QMessageBox.warning(
            self,
            title,
            text,
            QMessageBox.StandardButton.Ok,
        )

    def information_message_box(self, title: str, text: str):
        QMessageBox.information(
            self,
            title,
            text,
            QMessageBox.StandardButton.Ok,
        )

    def set_window_title(self, file: typing.Optional[Path] = None):
        title = "Bot Discord Easy Creator"
        if file and file.exists():
            title = f"Bot Discord Easy Creator - {file.name}"
        self.setWindowTitle(title)

    def on_new_action(self):
        config.set("file", "")
        config.save()
        interactions.clear()
        self.set_window_title()
        self.messages_list_widget.clear()

    def on_load_action(self):
        file_path, file_extension = QFileDialog.getOpenFileName(
            self,
            translate("MainWindow", "Open File"),
            os.getcwd(),
            "JSON Files (*.json)",
        )
        if file_path:
            file = Path(file_path)
            self.load_interactions(file)
            self.set_window_title(file)

    def saved_successfully_message_box(self):
        self.information_message_box(
            translate("MainWindow", "Saving"),
            translate(
                "MainWindow",
                "The file has been saved successfully.",
            ),
        )

    def on_save_action(self):
        file = Path(config.get("file"))
        if file.name == "":
            self.on_save_as_action()
        elif file.exists() and file.is_file():
            self.save()
        else:
            self.file_dont_exists_message_box()
            self.on_save_as_action()

    def save(self):
        interactions.save(Path(config.get("file")))
        self.saved_successfully_message_box()

    def file_dont_exists_message_box(self):
        self.warning_message_box(
            translate("MainWindow", "Warning"),
            translate("MainWindow", "The file don't exists anymore."),
        )

    def on_save_as_action(self):
        file_path, file_extension = QFileDialog.getSaveFileName(
            self,
            translate("MainWindow", "Save File"),
            os.getcwd(),
            "JSON Files (*.json)",
        )
        if file_path:
            config.set("file", file_path)
            config.save()
            path = Path(file_path)
            interactions.save(path)
            self.set_window_title(path)
            self.saved_successfully_message_box()

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
        self.warning_message_box(
            translate("MainWindow", "Warning"),
            translate(
                "MainWindow",
                "You need to restart the application to apply the changes.",
            ),
        )
        config.set("language", language)
        config.save()

    def start_turn_on_bot_thread(self):
        if config.get("token") == "":
            return self.on_login_failure()
        self.bot_thread.start()
        self.turn_on_bot_button.setDisabled(True)

    def on_bot_ready(self):
        self.turn_on_bot_button.setDisabled(False)
        self.update_bot_button()
        self.update_groups()

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

    def edit_selected_message(self):
        """Opens the NewMessage interface and loads saved information."""
        if self.__is_selecting_message():
            selected_message = self.__get_selected_message_text()
            self.message_window = EditMessageWindow(
                self, selected_message, interactions.get("messages")[selected_message]
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
        messages: dict = interactions.get("messages")
        messages.pop(old_message_name)
        messages[new_message_name] = message_data
        self.__get_list_item_message(old_message_name).setText(new_message_name)

    def accepted_new_message(self, message_name: str, message_data: dict):
        if not message_name:
            message_name = interactions.new_id()
        messages: dict = interactions.get("messages")
        messages[message_name] = message_data
        self.messages_list_widget.addItem(message_name)

    def __get_selected_message(self) -> int:
        return self.messages_list_widget.selectedIndexes()[0].row()

    def __get_selected_group(self) -> int:
        return self.groups_list_widget.selectedIndexes()[0].row()

    def __get_selected_group_user_data(self) -> int:
        return self.groups_list_widget.selectedIndexes()[0].data(
            Qt.ItemDataRole.UserRole
        )

    def __get_list_item_message(self, message: str) -> QListWidgetItem:
        return self.messages_list_widget.item(
            next(
                filter(
                    lambda i: self.messages_list_widget.item(i).text() == message,
                    range(self.messages_list_widget.count()),
                )
            )
        )

    def update_bot_button(self):
        on = self.bot_thread.isRunning()
        self.turn_on_bot_button.setHidden(on)
        self.turn_off_bot_button.setHidden(not on)

    def __get_selected_message_text(self) -> str:
        return self.messages_list_widget.selectedItems()[0].text()

    def __get_selected_group_text(self) -> str:
        return self.groups_list_widget.selectedItems()[0].text()

    def __is_selecting_message(self) -> bool:
        return bool(self.messages_list_widget.selectedIndexes())

    def __is_selecting_group(self) -> bool:
        return bool(self.groups_list_widget.selectedIndexes())

    def remove_selected_message(self):
        """Removes the selected message from the messages list and deletes it from "message and reply.json"."""
        selected_row = self.__get_selected_message()
        selected_message = self.__get_selected_message_text()
        self.messages_list_widget.takeItem(selected_row)
        messages = interactions.get("messages")
        messages.pop(selected_message)

    def confirm_remove_selected_message(self):
        """Asks the user if they want to remove the selected message."""
        if self.__is_selecting_message():
            self.confirm_message_box(
                translate("MainWindow", "Remove message"),
                translate(
                    "MainWindow", "Are you sure you want to remove this message?"
                ),
                self.remove_selected_message,
            )

    def confirm_remove_messages(self):
        """Asks the user if they want to remove all messages."""
        self.confirm_message_box(
            translate("MainWindow", "Remove all messages"),
            translate("MainWindow", "Are you sure you want to remove all messages?"),
            self.remove_messages,
        )

    def confirm_message_box(self, title: str, text: str, callback):
        dialog = QConfirmMessageBox(self)
        dialog.setWindowTitle(title)
        dialog.setText(text)
        dialog.accepted.connect(callback)
        dialog.exec()

    def remove_messages(self):
        """Removes all messages from the list."""
        self.messages_list_widget.clear()
        interactions.set("messages", {})

    def load_interactions(self, path: Path):
        """
        Loads all messages from file in path and inserts them into the messages list.
        If it's an invalid file raises a warning window.
        Saves the file path on config file if it's valid.
        """
        temp_interactions = Interactions()
        temp_interactions.load(path)
        if temp_interactions.is_valid():
            interactions.set("messages", temp_interactions.get("messages"))
            interactions.set("groups", temp_interactions.get("groups"))
            self.messages_list_widget.clear()
            for message_name in interactions.message_names():
                self.messages_list_widget.addItem(message_name)
            config.set("file", str(path))
            config.save()
        else:
            self.warning_message_box(
                translate("MainWindow", "Invalid file"),
                translate("MainWindow", "This file can't be loaded."),
            )

    def log(self, message: str, level: typing.Optional[int] = None):
        if level is None:
            level = logging.INFO
        styles = {
            logging.INFO: "",
            logging.DEBUG: "color: #E5D352;",
            logging.ERROR: "color: #D8315B;",
            logging.WARNING: "color: #FF7F11;",
        }
        text_cursor = self.logs_text_edit.textCursor()
        text_cursor.movePosition(
            QTextCursor.MoveOperation.End, QTextCursor.MoveMode.MoveAnchor
        )
        text_cursor.insertHtml(
            f'<span style="{styles[level]}">{html.escape(message)}</span><br>'
        )

    def turn_off_bot(self):
        self.bot_thread.close()
        self.turn_off_bot_button.setDisabled(True)

    def on_bot_thread_finished(self):
        self.turn_off_bot_button.setDisabled(False)
        self.update_bot_button()

    def closeEvent(self, event: QCloseEvent):
        if self.bot_thread.isRunning():
            self.turn_off_bot()
            self.setCursor(Qt.CursorShape.WaitCursor)
            self.bot_thread.quit()
            self.bot_thread.wait()
        event.accept()
