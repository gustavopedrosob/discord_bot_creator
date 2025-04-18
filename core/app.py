from core.translator import Translator
import locale
import logging
import os
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog
from discord.abc import Messageable

from controllers.credits import CreditsController
from controllers.group import GroupController
from controllers.main import MainController
from controllers.message import MessageController
from core.config import instance as config
from core.interactions import interactions


from views.credits.credits import CreditsView
from views.group.group import GroupView
from core.bot_thread import QBotThread
from views.main.log_handler import log_handler
from views.main.main import MainView
from views.messages.messages import MessageView


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
        self.main_controller = MainController(self.bot_thread)
        self.message_controller = MessageController()
        self.group_controller = GroupController()
        self.credits_controller = CreditsController()
        self.setup_binds(self.main_controller.view, self.message_controller.view, self.group_controller.view,
                         self.credits_controller.view)

    def setup_binds(self, main_view: MainView, message_view: MessageView, group_view: GroupView,
                    credits_view: CreditsView):
        main_view.menu_bar.help.credits.triggered.connect(credits_view.window.show)
        main_view.menu_bar.file.save_as.triggered.connect(self.on_save_as_action)
        main_view.menu_bar.file.save.triggered.connect(self.on_save_action)
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

            self.group_controller.config(
                str(selected_group_id),
                group_item.text(),
                group.text_channels,
                group.voice_channels,
                welcome_message_channel,
                welcome_message,
            )
            result = self.group_controller.view.window.exec()
            if result == QDialog.DialogCode.Accepted:
                self.on_save_action()

    def new_message(self):
        self.message_controller.current_message = None
        self.message_controller.config(
            "",
            {"expected message": [], "reply": [], "reaction": [], "conditions": [], "pin or del": None,
             "kick or ban": None, "where reply": None, "where reaction": None, "delay": 0})
        result = self.message_controller.view.window.exec()
        if result == "save":
            self.on_save_action()
        if result in ("save", QDialog.DialogCode.Accepted):
            self.main_controller.accepted_new_message(self.message_controller.get_name())

    def edit_selected_message(self):
        """Opens the NewMessage interface and loads saved information."""
        if bool(self.main_controller.view.messages_list_widget.selectedIndexes()):
            selected_message = self.main_controller.view.messages_list_widget.selectedItems()[0].text()
            self.message_controller.current_message = selected_message
            self.message_controller.config(selected_message, interactions.get("messages")[selected_message])
            result = self.message_controller.view.window.exec()
            if result == "save":
                self.on_save_action()
            if result in ("save", QDialog.DialogCode.Accepted):
                self.main_controller.accepted_edit_selected_message(selected_message, self.message_controller.get_name())

    def on_save_as_action(self):
        file_path, file_extension = QFileDialog.getSaveFileName(
            self.main_controller.view.window,
            Translator.translate("MainWindow", "Save File"),
            os.getcwd(),
            "JSON Files (*.json)",
        )
        if file_path:
            config.set("file", file_path)
            config.save()
            path = Path(file_path)
            interactions.save(path)
            self.main_controller.set_window_title(path)
            self.main_controller.saved_successfully_message_box()

    def save(self):
        interactions.save(Path(config.get("file")))
        self.main_controller.saved_successfully_message_box()

    def on_save_action(self):
        file = Path(config.get("file"))
        if file.name == "":
            self.on_save_as_action()
        elif file.exists() and file.is_file():
            self.save()
        else:
            self.main_controller.file_dont_exists_message_box()
            self.on_save_as_action()
