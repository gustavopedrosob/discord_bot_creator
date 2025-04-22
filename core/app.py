from typing import Union

from core.database import Database
from core.translator import Translator
import locale
import logging
import os
import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox
from controllers.credits import CreditsController
from controllers.group import GroupController
from controllers.main import MainController
from controllers.message import MessageController
from core.config import instance as config
from views.credits import CreditsView
from core.bot_thread import QBotThread
from widgets.log_handler import log_handler
from views.main import MainView


logger = logging.getLogger(__name__)
logger.addHandler(log_handler)


class Application(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        logging.basicConfig(
            level=config.get("log_level"),
            format="%(asctime)s - %(message)s",
            datefmt="%x %X",
        )
        lang = config.get("language")
        locale.setlocale(locale.LC_ALL, lang)
        self.installTranslator(Translator.get_instance())
        self.bot_thread = QBotThread()
        log_handler.set_signal(self.bot_thread.log)
        self.database = Database(self.get_database_path())
        self.main_controller = MainController(self.database, self.bot_thread)
        self.message_controller = MessageController(self.database)
        self.group_controller = GroupController(self.database)
        self.credits_controller = CreditsController()
        self.setup_binds(
            self.main_controller.view,
            self.credits_controller.view,
        )
        self.main_controller.load_data()

    def on_new_action(self):
        config.set("database", ":memory:")
        config.save()
        self.database.new_session(":memory:")
        self.main_controller.load_data()

    def get_database_path(self) -> str:
        database_path = Path(config.get("database"))
        if database_path.name == ":memory:":
            return ":memory:"
        elif database_path.exists() and database_path.is_file():
            return str(database_path)
        else:
            self.file_dont_exists_message_box()
            return ":memory:"

    def setup_binds(
        self,
        main_view: MainView,
        credits_view: CreditsView,
    ):
        main_view.menu_bar.help.credits.triggered.connect(credits_view.window.show)
        main_view.menu_bar.file.save_as.triggered.connect(self.on_save_as_action)
        main_view.menu_bar.file.save.triggered.connect(self.on_save_action)
        main_view.menu_bar.file.new.triggered.connect(self.on_new_action)
        main_view.new_message_button.clicked.connect(self.new_message)
        main_view.edit_messages_button.clicked.connect(self.edit_selected_message)
        main_view.messages_list_widget.new_action.triggered.connect(self.new_message)
        main_view.messages_list_widget.edit_action.triggered.connect(
            self.edit_selected_message
        )
        main_view.groups_list_widget.config_action.triggered.connect(
            self.config_selected_group
        )
        main_view.config_group_button.clicked.connect(self.config_selected_group)

    def config_selected_group(self):
        if bool(self.main_controller.view.groups_list_widget.selectedIndexes()):
            group_item = self.main_controller.view.groups_list_widget.selectedItems()[0]
            selected_group_id = group_item.data(Qt.ItemDataRole.UserRole)
            group = self.bot_thread.groups()[selected_group_id]
            group_interaction = self.database.get_group(group.id)
            self.group_controller.config(
                group,
                group_interaction,
            )
            result = self.group_controller.view.window.exec()
            if result == QDialog.DialogCode.Accepted:
                self.on_save_action()

    def new_message(self):
        self.message_controller.reset()
        result = self.message_controller.view.window.exec()
        if result == 2:
            self.on_save_action()
        if result in (2, QDialog.DialogCode.Accepted):
            self.main_controller.accepted_new_message(
                self.message_controller.get_name()
            )

    def edit_selected_message(self):
        """Opens the NewMessage interface and loads saved information."""
        if bool(self.main_controller.view.messages_list_widget.selectedIndexes()):
            selected_message = (
                self.main_controller.view.messages_list_widget.selectedItems()[0].text()
            )
            self.message_controller.config(self.database.get_message(selected_message))
            result = self.message_controller.view.window.exec()
            if result == 2:
                self.on_save_action()
            if result in (2, QDialog.DialogCode.Accepted):
                self.main_controller.accepted_edit_selected_message(
                    selected_message, self.message_controller.get_name()
                )

    def on_save_as_action(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_controller.view.window,
            Translator.translate("MainWindow", "Save File"),
            os.getcwd(),
            "DB Files (*.db)",
        )
        if file_path:
            self.save(file_path)

    def save(self, path: Union[Path, str, None] = None):
        self.database.commit()
        if path:
            path = Path(path)
            config.set("database", str(path))
            config.save()
            self.database.backup(path)
            self.main_controller.update_window_title()
        self.main_controller.saved_successfully_message_box()

    @staticmethod
    def file_dont_exists_message_box():
        msg = QMessageBox()
        msg.setWindowTitle(Translator.translate("MainWindow", "Warning"))
        msg.setText(
            Translator.translate("MainWindow", "The file don't exists anymore.")
        )
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.exec()

    def on_save_action(self):
        database_path = Path(config.get("database"))
        if database_path.name == ":memory:":
            self.on_save_as_action()
        else:
            self.save()
