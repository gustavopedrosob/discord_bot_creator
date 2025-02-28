import webbrowser

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QWidget

translate = QCoreApplication.translate


class QHelpMenu(QMenu):
    def __init__(self, text: str, parent: QWidget):
        super().__init__(text, parent)
        self.credits = QAction(translate("MainWindow", "Credits"), self)
        self.project = QAction(translate("MainWindow", "Project"), self)
        self.report = QAction(translate("MainWindow", "Report bug"), self)
        self.discord_applications = QAction(
            translate("MainWindow", "Discord applications"), self
        )

        self.setup_actions()
        self.setup_binds()

    def setup_actions(self):
        self.addActions(
            (
                self.discord_applications,
                self.credits,
                self.project,
                self.report,
            )
        )

    def setup_binds(self):
        self.discord_applications.triggered.connect(
            lambda: webbrowser.open("https://discord.com/developers/applications/")
        )
        self.report.triggered.connect(
            lambda: webbrowser.open(
                "https://github.com/gustavopedrosob/bot_discord_easy_creator/issues/new"
            )
        )
        self.project.triggered.connect(
            lambda: webbrowser.open(
                "https://github.com/gustavopedrosob/bot_discord_easy_creator"
            )
        )
