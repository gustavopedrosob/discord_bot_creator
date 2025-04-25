from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QMainWindow,
    QTabWidget, QSplitter,
)
from extra_qwidgets.utils import get_awesome_icon, colorize_icon
from extra_qwidgets.widgets.color_button import QColorButton
from extra_qwidgets.widgets.password import QPassword

from core.config import instance as config
from widgets.custom_button import QCustomButton
from widgets.groups_list import QGroupsList
from widgets.log_textedit import QLogTextEdit
from widgets.menu_bar import MenuBar
from widgets.messages_list import QMessagesList

translate = QCoreApplication.translate


class MainView:
    def __init__(self):
        self.window = QMainWindow()
        self.window.setMinimumSize(800, 600)
        self.window.resize(1000, 800)
        self.window.setWindowIcon(QIcon("source/icons/window-icon.svg"))

        self.menu_bar = MenuBar(self.window)

        self.logs_text_edit = QLogTextEdit()

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

        self.setup_layout()
        self.setup_menus()
        self.window.show()

    def setup_menus(self):
        self.window.setMenuBar(self.menu_bar)
        self.window.addActions(
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
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.window.setCentralWidget(splitter)
        right_frame = QVBoxLayout()
        right_widget = QWidget()
        right_widget.setMinimumWidth(520)
        right_widget.setLayout(right_frame)
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
        left_widget.setMinimumWidth(280)
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
        right_frame.setContentsMargins(10, 10, 10, 10)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(1, 1)
