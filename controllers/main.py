import logging
import os
import typing
from pathlib import Path
import html

from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QTextCursor, QCloseEvent
from PySide6.QtWidgets import QMessageBox, QListWidgetItem, QFileDialog

from core.config import instance as config
from core.interactions import interactions, Interactions
from views.classes.confirm_message_box import QConfirmMessageBox
from core.bot_thread import QBotThread
from views.main.main import MainView


translate = QCoreApplication.translate


class MainController:
    def __init__(self, bot_thread: QBotThread):
        self.view = MainView()
        self.bot_thread = bot_thread

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
        self.update_bot_button()

    def setup_binds(self):
        self.view.remove_message_button.clicked.connect(self.confirm_remove_selected_message)
        self.view.remove_all_message_button.clicked.connect(self.confirm_remove_messages)
        self.view.turn_on_bot_button.clicked.connect(self.start_turn_on_bot_thread)
        self.view.turn_off_bot_button.clicked.connect(self.turn_off_bot)
        self.__setup_message_list_binds(self.view.messages_list_widget)
        self.__setup_menu_bar_binds(self.view.menu_bar)
        self.__setup_bot_thread_binds(self.bot_thread)
        self.view.groups_list_widget.quit_action.triggered.connect(self.quit_selected_group)
        self.view.quit_group_button.clicked.connect(self.quit_selected_group)
        self.view.token_widget.line_edit.textEdited.connect(self.update_token)
        # noinspection PyUnresolvedReferences
        self.view.cmd_combobox.lineEdit().returnPressed.connect(self.entry_command)
        self.view.window.close_event = self.close_event

    def __setup_menu_bar_binds(self, menu_bar):
        menu_bar.file.exit.triggered.connect(self.view.window.close)
        menu_bar.file.load.triggered.connect(self.on_load_action)
        menu_bar.file.new.triggered.connect(self.on_new_action)
        menu_bar.config.language.english.triggered.connect(
            lambda: self.set_language("en_us")
        )
        menu_bar.config.language.portuguese.triggered.connect(
            lambda: self.set_language("pt_br")
        )

    def __setup_message_list_binds(self, message_list):
        message_list.remove_action.triggered.connect(
            self.confirm_remove_selected_message
        )
        message_list.remove_all_action.triggered.connect(
            self.confirm_remove_messages
        )

    def __setup_bot_thread_binds(self, bot_thread):
        bot_thread.finished.connect(self.on_bot_thread_finished)
        bot_thread.bot_ready.connect(self.on_bot_ready)
        bot_thread.login_failure.connect(self.on_login_failure)
        bot_thread.log.connect(self.log)
        bot_thread.guild_join.connect(self.update_groups)
        bot_thread.guild_remove.connect(self.update_groups)
        bot_thread.guild_update.connect(self.update_groups)

    def quit_selected_group(self):
        selection = self.view.groups_list_widget.selectedIndexes()
        if bool(selection):
            item = self.view.groups_list_widget.item(selection[0].row())
            group_id = item.data(Qt.ItemDataRole.UserRole)
            self.view.groups_list_widget.takeItem(selection[0].row())
            self.bot_thread.leave_group(group_id)

    def update_groups(self):
        self.view.groups_list_widget.clear()
        for group_id, group in self.bot_thread.groups().items():
            group = QListWidgetItem(group.name)
            group.setData(Qt.ItemDataRole.UserRole, group_id)
            self.view.groups_list_widget.addItem(group)

    def on_login_failure(self):
        self.warning_message_box(
            translate("MainWindow", "Login failure"),
            translate("MainWindow", "Improper token has been passed."),
        )
        self.view.turn_on_bot_button.setDisabled(False)

    def warning_message_box(self, title: str, text: str):
        QMessageBox.warning(
            self.view.window,
            title,
            text,
            QMessageBox.StandardButton.Ok,
        )

    def information_message_box(self, title: str, text: str):
        QMessageBox.information(
            self.view.window,
            title,
            text,
            QMessageBox.StandardButton.Ok,
        )

    def set_window_title(self, file: typing.Optional[Path] = None):
        title = "Discord Bot Creator"
        if file and file.exists():
            title = f"Discord Bot Creator - {file.name}"
        self.view.window.setWindowTitle(title)

    def on_new_action(self):
        config.set("file", "")
        config.save()
        interactions.clear()
        self.set_window_title()
        self.view.messages_list_widget.clear()

    def on_load_action(self):
        file_path, file_extension = QFileDialog.getOpenFileName(
            self.view.window,
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

    def file_dont_exists_message_box(self):
        self.warning_message_box(
            translate("MainWindow", "Warning"),
            translate("MainWindow", "The file don't exists anymore."),
        )

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
            self.on_login_failure()
        else:
            self.bot_thread.start()
            self.view.turn_on_bot_button.setDisabled(True)

    def on_bot_ready(self):
        self.view.turn_on_bot_button.setDisabled(False)
        self.update_bot_button()
        self.update_groups()

    def entry_command(self):
        """Handles commands for the bot's log entry."""
        cmd = self.view.cmd_combobox.lineEdit().text()
        if cmd in ["cls", "clear"]:
            self.view.logs_text_edit.clear()
            self.view.cmd_combobox.clear()

    def update_token(self):
        """Updates the token in the "config.json" file and in the interface."""
        token = self.view.token_widget.line_edit.text()
        config.set("token", token)
        config.save()

    def get_selected_message(self) -> typing.Optional[str]:
        if bool(self.view.messages_list_widget.selectedIndexes()):
            return self.view.messages_list_widget.selectedItems()[0].text()
        return None

    def __get_list_item_message(self, message: str) -> typing.Optional[QListWidgetItem]:
        for i in self.view.messages_list_widget.selectedItems():
            if i.text() == message:
                return i
            return None
        return None

    def update_bot_button(self):
        on = self.bot_thread.isRunning()
        self.view.turn_on_bot_button.setHidden(on)
        self.view.turn_off_bot_button.setHidden(not on)

    def remove_selected_message(self):
        """Removes the selected message from the message list and deletes it from "message and reply.json"."""
        message_indexes = self.view.messages_list_widget.selectedIndexes()
        if message_indexes:
            row = message_indexes[0].row()
            messages = interactions.get("messages")
            messages.pop(self.view.messages_list_widget.item(row).text())
            self.view.messages_list_widget.takeItem(row)

    def confirm_remove_selected_message(self):
        """Asks the user if they want to remove the selected message."""
        if bool(self.view.messages_list_widget.selectedIndexes()):
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
        dialog = QConfirmMessageBox(self.view.window)
        dialog.setWindowTitle(title)
        dialog.setText(text)
        dialog.accepted.connect(callback)
        dialog.exec()

    def remove_messages(self):
        """Removes all messages from the list."""
        self.view.messages_list_widget.clear()
        interactions.set("messages", {})

    def load_interactions(self, path: Path):
        """
        Loads all messages from a file in a path and inserts them into the message list.
        If it's an invalid file raises a warning window.
        Saves the file path on a config file if it's valid.
        """
        temp_interactions = Interactions()
        temp_interactions.load(path)
        if temp_interactions.is_valid():
            interactions.set("messages", temp_interactions.get("messages"))
            interactions.set("groups", temp_interactions.get("groups"))
            self.view.messages_list_widget.clear()
            for message_name in interactions.message_names():
                self.view.messages_list_widget.addItem(message_name)
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
        text_cursor = self.view.logs_text_edit.textCursor()
        text_cursor.movePosition(
            QTextCursor.MoveOperation.End, QTextCursor.MoveMode.MoveAnchor
        )
        text_cursor.insertHtml(
            f'<span style="{styles[level]}">{html.escape(message)}</span><br>'
        )

    def accepted_edit_selected_message(self, old_message_name: str, new_message_name: str):
        self.__get_list_item_message(old_message_name).setText(new_message_name)

    def accepted_new_message(self, message_name: str):
        self.view.messages_list_widget.addItem(message_name)

    def turn_off_bot(self):
        self.bot_thread.close()
        self.view.turn_off_bot_button.setDisabled(True)

    def on_bot_thread_finished(self):
        self.view.turn_off_bot_button.setDisabled(False)
        self.update_bot_button()

    def close_event(self, event: QCloseEvent):
        if self.bot_thread.isRunning():
            self.turn_off_bot()
            self.view.window.setCursor(Qt.CursorShape.WaitCursor)
            self.bot_thread.quit()
            self.bot_thread.wait()
        event.accept()