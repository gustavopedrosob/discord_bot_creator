import logging
import os
import typing
import webbrowser
from pathlib import Path
from threading import Thread

from PySide6.QtCore import QPoint, QCoreApplication
from PySide6.QtGui import QIcon, QAction, Qt
from PySide6.QtWidgets import (
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
    QFileDialog,
    QMainWindow,
)

from bot import IntegratedBot
from core.config import instance as config
from core.messages import messages, Messages
from interfaces.classes.color_button import QColorButton
from interfaces.classes.qpassword import QPassword
from interfaces.credits.credits import CreditsWindow
from interfaces.main.log_handler import LogHandler
from interfaces.newmessage.main import EditMessageWindow, NewMessageWindow

logger = logging.getLogger(__name__)
translate = QCoreApplication.translate


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.resize(1000, 800)
        self.setWindowIcon(QIcon("source/icons/window-icon.svg"))

        self.message_window = None
        self.credits_window = CreditsWindow()
        self.bot = None
        self.bot_thread = None
        self.bot_on = False

        log_handler = LogHandler(self)
        log_handler.setLevel(logging.INFO)
        logger.addHandler(log_handler)

        # Create the menu bar
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # Create menus
        file_menu = QMenu(translate("MainWindow", "File"), self)
        config_menu = QMenu(translate("MainWindow", "Config"), self)
        edit_menu = QMenu(translate("MainWindow", "Edit"), self)
        help_menu = QMenu(translate("MainWindow", "Help"), self)

        # Add menus to the menu bar
        self.menu_bar.addMenu(file_menu)
        self.menu_bar.addMenu(config_menu)
        self.menu_bar.addMenu(edit_menu)
        self.menu_bar.addMenu(help_menu)

        language_menu = QMenu(translate("MainWindow", "Language"), self)
        config_menu.addMenu(language_menu)

        english_action = QAction(translate("MainWindow", "English"), self)
        english_action.triggered.connect(lambda: self.set_language("en_us"))
        portuguese_action = QAction(translate("MainWindow", "Portuguese"), self)
        portuguese_action.triggered.connect(lambda: self.set_language("pt_br"))
        language_menu.addAction(english_action)
        language_menu.addAction(portuguese_action)

        new_action = QAction(translate("MainWindow", "New file"), self)
        new_action.triggered.connect(self.on_new_action)
        load_action = QAction(translate("MainWindow", "Load"), self)
        load_action.triggered.connect(self.on_load_action)
        save_action = QAction(translate("MainWindow", "Save"), self)
        save_action.triggered.connect(self.on_save_action)
        save_as_action = QAction(translate("MainWindow", "Save as"), self)
        save_as_action.triggered.connect(self.on_save_as_action)
        exit_action = QAction(translate("MainWindow", "Exit"), self)
        exit_action.triggered.connect(self.close)

        for action in [
            new_action,
            load_action,
            save_action,
            save_as_action,
            exit_action,
        ]:
            file_menu.addAction(action)

        credits_action = QAction(translate("MainWindow", "Credits"), self)
        credits_action.triggered.connect(self.credits_window.window.show)
        project_action = QAction(translate("MainWindow", "Project"), self)
        project_action.triggered.connect(
            lambda: webbrowser.open(
                "https://github.com/gustavopedrosob/bot_discord_easy_creator"
            )
        )
        report_action = QAction(translate("MainWindow", "Report bug"), self)
        report_action.triggered.connect(
            lambda: webbrowser.open(
                "https://github.com/gustavopedrosob/bot_discord_easy_creator/issues/new"
            )
        )
        discord_applications = QAction(
            translate("MainWindow", "Discord applications"), self
        )
        discord_applications.triggered.connect(
            lambda: webbrowser.open("https://discord.com/developers/applications/")
        )
        self.new_message_action = QAction(translate("MainWindow", "New message"), self)
        self.new_message_action.triggered.connect(self.new_message)
        self.new_message_action.setShortcut("Ctrl+N")
        self.edit_message_action = QAction(
            translate("MainWindow", "Edit message"), self
        )
        self.edit_message_action.triggered.connect(self.edit_selected_message)
        self.edit_message_action.setShortcut("Ctrl+E")
        self.remove_selected_message_action = QAction(
            translate("MainWindow", "Remove message"), self
        )
        self.remove_selected_message_action.triggered.connect(
            self.confirm_remove_selected_message
        )
        self.remove_selected_message_action.setShortcut("Delete")
        self.remove_all_message_action = QAction(
            translate("MainWindow", "Remove all messages"), self
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
            translate("MainWindow", "No logs at moment")
        )
        self.logs_text_edit.setReadOnly(True)
        self.logs_text_edit.setFocusPolicy(Qt.FocusPolicy.NoFocus)

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
        self.token_widget.line_edit.textEdited.connect(self.update_token)
        self.token_widget.line_edit.setMaxLength(100)

        # Execute Bot Button
        self.turn_on_bot_button = QColorButton(
            translate("MainWindow", "Turn on bot"), "#3e92cc"
        )
        self.turn_on_bot_button.setIcon(QIcon("source/icons/play-solid.svg"))
        self.turn_on_bot_button.clicked.connect(self.start_turn_on_bot_thread)
        self.turn_off_bot_button = QColorButton(
            translate("MainWindow", "Turn off bot"), "#d8315b"
        )
        self.turn_off_bot_button.setIcon(QIcon("source/icons/stop-solid.svg"))
        self.turn_off_bot_button.clicked.connect(self.turn_off_bot)
        self.set_switch_bot_button(False)

        # Adding Widgets to Right Frame
        right_frame.addWidget(self.logs_text_edit)
        right_frame.addWidget(self.cmd_combobox)
        right_frame.addWidget(QLabel("Token:"))
        right_frame.addWidget(self.token_widget)
        right_frame.addWidget(self.turn_on_bot_button)
        right_frame.addWidget(self.turn_off_bot_button)

        # Left Frame for Messages
        left_frame = QVBoxLayout()

        message_label = QLabel(translate("MainWindow", "Messages"))

        self.messages_list_widget = QListWidget()
        self.messages_list_widget.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.messages_list_widget.customContextMenuRequested.connect(
            self.message_context_menu_event
        )

        new_message_button = QPushButton(translate("MainWindow", "New"))
        new_message_button.clicked.connect(self.new_message)

        edit_messages_button = QPushButton(translate("MainWindow", "Edit"))
        edit_messages_button.clicked.connect(self.edit_selected_message)

        remove_message_button = QPushButton(translate("MainWindow", "Remove"))
        remove_message_button.clicked.connect(self.confirm_remove_selected_message)

        remove_all_message_button = QPushButton(translate("MainWindow", "Remove all"))
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

        file = Path(config.get("file"))

        if file.name == "":
            self.set_window_title()
        elif file.exists() and file.is_file():
            self.load_messages(file)
            self.set_window_title(file)
        else:
            self.file_dont_exists_message_box()
            config.set("file", "")
            config.save()
            self.set_window_title()

    def set_window_title(self, file: typing.Optional[Path] = None):
        title = "Bot Discord Easy Creator"
        if file and file.exists():
            title = f"Bot Discord Easy Creator - {file.name}"
        self.setWindowTitle(title)

    def on_new_action(self):
        config.set("file", "")
        config.save()
        messages.clear()
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
            self.load_messages(file)
            self.set_window_title(file)

    def saved_successfully_message_box(self):
        warning = QMessageBox(self)
        warning.setWindowTitle(translate("MainWindow", "Saving"))
        warning.setText(
            translate(
                "MainWindow",
                "The file has been saved successfully.",
            )
        )
        warning.exec()

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
        messages.save(Path(config.get("file")))
        self.saved_successfully_message_box()

    def file_dont_exists_message_box(self):
        warning = QMessageBox(self)
        warning.setWindowTitle(translate("MainWindow", "Warning"))
        warning.setText(
            translate(
                "MainWindow",
                "The file don't exists anymore.",
            )
        )
        warning.exec()

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
            messages.save(path)
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
        warning = QMessageBox(self)
        warning.setWindowTitle(translate("MainWindow", "Warning"))
        warning.setText(
            translate(
                "MainWindow",
                "You need to restart the application to apply the changes.",
            )
        )
        warning.exec()
        config.set("language", language)
        config.save()

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
        self.__get_list_item_message(old_message_name).setText(new_message_name)

    def accepted_new_message(self, message_name: str, message_data: dict):
        if not message_name:
            message_name = messages.new_id()
        messages.set(message_name, message_data)
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

    def set_switch_bot_button(self, on: bool):
        self.bot_on = on
        self.turn_on_bot_button.setHidden(on)
        self.turn_off_bot_button.setHidden(not on)

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

    def confirm_remove_selected_message(self):
        """Asks the user if they want to remove the selected message."""
        if self.__is_selecting_message():
            dialog = QMessageBox(self)
            dialog.setWindowTitle(translate("MainWindow", "Remove message"))
            dialog.setText(
                translate("MainWindow", "Are you sure you want to remove this message?")
            )
            dialog.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            yes_button = dialog.button(QMessageBox.StandardButton.Yes)
            yes_button.setText(translate("MainWindow", "Yes"))
            no_button = dialog.button(QMessageBox.StandardButton.No)
            no_button.setText(translate("MainWindow", "No"))
            dialog.setDefaultButton(QMessageBox.StandardButton.No)
            dialog.accepted.connect(self.remove_selected_message)
            dialog.exec()

    def confirm_remove_messages(self):
        """Asks the user if they want to remove all messages."""
        dialog = QMessageBox(self)
        dialog.setWindowTitle(translate("MainWindow", "Remove all messages"))
        dialog.setText(
            translate("MainWindow", "Are you sure you want to remove all messages?")
        )
        dialog.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        yes_button = dialog.button(QMessageBox.StandardButton.Yes)
        yes_button.setText(translate("MainWindow", "Yes"))
        no_button = dialog.button(QMessageBox.StandardButton.No)
        no_button.setText(translate("MainWindow", "No"))
        dialog.setDefaultButton(QMessageBox.StandardButton.No)
        dialog.accepted.connect(self.remove_messages)
        dialog.exec()

    def remove_messages(self):
        """Removes all messages from the list."""
        self.messages_list_widget.clear()
        messages.clear()

    def load_messages(self, path: Path):
        """
        Loads all messages from file in path and inserts them into the messages list.
        If it's an invalid file raises a warning window.
        Saves the file path on config file if it's valid.
        """
        temp_messages = Messages()
        temp_messages.load(path)
        if temp_messages.is_valid():
            messages.replace(temp_messages)
            self.messages_list_widget.clear()
            for message_name in messages.message_names():
                self.messages_list_widget.addItem(message_name)
            config.set("file", str(path))
            config.save()
        else:
            QMessageBox.warning(
                self,
                translate("MainWindow", "Invalid file"),
                translate("MainWindow", "This file can't be loaded."),
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.NoButton,
            )

    def log(self, message):
        self.logs_text_edit.insertPlainText(message)
        self.logs_text_edit.update()

    def turn_off_bot(self):
        self.bot.loop.create_task(self.bot.close())
        self.setCursor(Qt.CursorShape.WaitCursor)
        self.bot_thread.join()
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.set_switch_bot_button(False)

    def message_context_menu_event(self, position: QPoint):
        context_menu = QMenu(self)
        context_menu.addAction(self.new_message_action)
        if self.__is_selecting_message():
            context_menu.addAction(self.edit_message_action)
            context_menu.addAction(self.remove_selected_message_action)
        context_menu.addAction(self.remove_all_message_action)
        context_menu.exec(self.messages_list_widget.mapToGlobal(position))

    def closeEvent(self, event):
        if self.bot_on:
            self.turn_off_bot()
        super().closeEvent(event)
