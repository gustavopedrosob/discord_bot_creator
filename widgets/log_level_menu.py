import logging

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QWidget, QMenu

from core.config import Config
from core.functions import config_log_level

translate = QCoreApplication.translate


class QLogLevelMenu(QMenu):
    def __init__(self, text: str, parent: QWidget):
        super().__init__(text, parent)

        log_level = Config.get("log_level")
        self.action_group = QActionGroup(self)
        self.action_group.setExclusive(True)

        self.debug_level_action = QAction(
            translate("MainWindow", "Debug"),
            self,
            checked=log_level == logging.DEBUG,
            checkable=True,
        )
        self.info_level_action = QAction(
            translate("MainWindow", "Info"),
            self,
            checked=log_level == logging.INFO,
            checkable=True,
        )
        self.warning_level_action = QAction(
            translate("MainWindow", "Warning"),
            self,
            checked=log_level == logging.WARNING,
            checkable=True,
        )
        self.error_level_action = QAction(
            translate("MainWindow", "Error"),
            self,
            checked=log_level == logging.ERROR,
            checkable=True,
        )

        self.setup_actions()
        self.setup_binds()

    def setup_actions(self):
        log_level_actions = (
            self.debug_level_action,
            self.info_level_action,
            self.warning_level_action,
            self.error_level_action,
        )
        self.addActions(log_level_actions)
        for a in log_level_actions:
            self.action_group.addAction(a)

    def setup_binds(self):
        self.error_level_action.triggered.connect(
            lambda: config_log_level(logging.ERROR)
        )
        self.warning_level_action.triggered.connect(
            lambda: config_log_level(logging.WARNING)
        )
        self.info_level_action.triggered.connect(lambda: config_log_level(logging.INFO))
        self.debug_level_action.triggered.connect(
            lambda: config_log_level(logging.DEBUG)
        )
