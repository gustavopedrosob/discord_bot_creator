import locale
import logging
import os
import sys
from pathlib import Path
from typing import Union

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog
from qfluentwidgets import setTheme, Theme, toggleTheme

from controllers.credits import CreditsController
from controllers.group import GroupController
from controllers.logs import LogsController
from controllers.main import MainController
from controllers.message import MessageController
from core.bot_thread import QBotThread
from core.config import Config
from core.database import Database
from core.log_handler import LogHandler
from core.translator import Translator
from views.credits import CreditsView
from views.main import MainView

logger = logging.getLogger(__name__)
logger.addHandler(LogHandler())


class Application(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        logging.basicConfig(
            level=Config.get("log_level"),
            format="%(asctime)s - %(message)s",
            datefmt="%x %X",
        )
        lang = Config.get("language")
        locale.setlocale(locale.LC_ALL, lang)
        self.installTranslator(Translator().get_instance())
        self.bot_thread = QBotThread()
        LogHandler().set_signal(self.bot_thread.log)

        self.database = Database()
        self.main_controller = MainController(self.database, self.bot_thread)
        self.logs_controller = LogsController(self.database)
        self.message_controller = MessageController(self.database)
        self.group_controller = GroupController(self.database)
        self.credits_controller = CreditsController()
        self.setup_binds(
            self.main_controller.view,
            self.credits_controller.view,
        )
        setTheme(Theme.AUTO)
        QTimer.singleShot(0, self.on_app_ready)

    @staticmethod
    def _on_theme_change():
        toggleTheme()

    def on_app_ready(self):
        Config.set("database", self.get_database_path())
        Config.save()
        self.database.update_session()
        self.main_controller.load_data()
        self.logs_controller.load_data()
        if Config.get("auto_start_bot"):
            self.main_controller.start_turn_on_bot_thread()

    def on_new_action(self):
        Config.set("database", ":memory:")
        Config.save()
        self.database.update_session()
        self.main_controller.load_data()

    def get_database_path(self) -> str:
        database_path = Path(Config.get("database"))
        if database_path.name == ":memory:":
            return ":memory:"
        elif database_path.exists() and database_path.is_file():
            return str(database_path)
        else:
            self.main_controller.file_dont_exists_message_box()
            return ":memory:"

    def on_opening_logs_window(self):
        self.logs_controller.view.window.show()
        self.logs_controller.update_logs_by_filters()

    def setup_binds(
        self,
        main_view: MainView,
        credits_view: CreditsView,
    ):
        QApplication.styleHints().colorSchemeChanged.connect(self._on_theme_change)
        main_view.menu_bar.help.credits.triggered.connect(credits_view.window.show)
        main_view.menu_bar.help.logs.triggered.connect(self.on_opening_logs_window)
        main_view.menu_bar.file.save_as.triggered.connect(self.on_save_as_action)
        main_view.menu_bar.file.save.triggered.connect(self.on_save_action)
        main_view.menu_bar.file.new.triggered.connect(self.on_new_action)
        main_view.new_message_button.clicked.connect(self.new_message)
        main_view.edit_messages_button.clicked.connect(self.edit_selected_message)
        main_view.messages_list_widget.new_action.triggered.connect(self.new_message)
        main_view.messages_list_widget.edit_action.triggered.connect(
            self.edit_selected_message
        )
        main_view.messages_list_widget.itemDoubleClicked.connect(
            self.edit_selected_message
        )
        main_view.groups_list_widget.config_action.triggered.connect(
            self.config_selected_group
        )
        main_view.groups_list_widget.itemDoubleClicked.connect(
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
        self.message_controller.config()
        result = self.message_controller.view.window.exec()
        if result == 2:
            self.on_save_action()
        if result in (2, QDialog.DialogCode.Accepted):
            self.main_controller.accepted_new_message(
                self.message_controller.current_message.name
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
            Config.set("database", str(path))
            Config.save()
            self.database.backup(path)
        self.main_controller.update_window_title()
        self.main_controller.saved_successfully_message_box()

    def on_save_action(self):
        database_path = Path(Config.get("database"))
        if database_path.name == ":memory:":
            self.on_save_as_action()
        else:
            self.save()
