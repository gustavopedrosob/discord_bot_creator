from PySide6.QtCore import QLocale
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QHeaderView

from core.database import Database
from core.translator import Translator, LOGGING_TRANSLATIONS
from models.log import Log
from views.logs import LogsView
from core.config import instance as config


class LogsController:
    def __init__(self, database: Database):
        self.view = LogsView()
        self.logs_model = QStandardItemModel()
        self.logs_model.setHorizontalHeaderLabels(
            [
                Translator.translate("LogsWindow", "Date"),
                Translator.translate("LogsWindow", "Message"),
                Translator.translate("LogsWindow", "Level"),
            ]
        )

        self.view.logs_table.setModel(self.logs_model)
        self.database = database
        self._add_log_level_options()
        self._setup_binds()
        self._set_date_format()

    def _add_log_level_options(self):
        self.view.level_filter.addItem(
            Translator.translate("LogsWindow", "All"), userData=None
        )
        for log_level, translation in LOGGING_TRANSLATIONS.items():
            self.view.level_filter.addItem(translation, userData=log_level)

    def _setup_binds(self):
        self.view.filter_button.clicked.connect(self.on_filter)
        self.view.reset_filter_button.clicked.connect(self.reset)

    def on_filter(self):
        self.update_logs_by_filters()

    def update_logs_by_filters(self):
        self.reset_table()
        self.load_data()

    def reset(self):
        self.reset_filters()
        self.update_logs_by_filters()

    def load_data(self):
        for log in self.database.get_logs(
            self.view.message_filter.text(),
            self.view.date_filter.getDate(),
            self.view.level_filter.currentData(),
        ):
            self.add_log(log)
        self._resize_columns()

    def _resize_columns(self):
        self.view.logs_table.resizeColumnsToContents()
        header = self.view.logs_table.horizontalHeader()
        column_count = self.view.logs_table.model().columnCount()
        for col in range(column_count - 1):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(column_count - 1, QHeaderView.ResizeMode.Stretch)

    def reset_table(self):
        self.logs_model.setRowCount(0)

    def reset_filters(self):
        self.view.level_filter.setCurrentIndex(0)
        self.view.message_filter.setText("")
        self.view.date_filter.reset()
        self.view.date_filter.setText(Translator.translate("LogsWindow", "Date"))

    def add_log(self, log: Log):
        date = QStandardItem(log.datetime.strftime("%x %X"))
        date.setEditable(False)
        message = QStandardItem(log.message)
        message.setEditable(False)
        level = QStandardItem(LOGGING_TRANSLATIONS[log.level_number])
        level.setEditable(False)
        self.logs_model.appendRow((date, message, level))

    def _set_date_format(self):
        lang = config.get("language")
        if lang == "pt_br":
            locale = QLocale(QLocale.Language.Portuguese, QLocale.Country.Brazil)
        elif lang == "en_us":
            locale = QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)
        else:
            locale = QLocale()
        fmt = locale.dateFormat(QLocale.FormatType.ShortFormat)
        self.view.date_filter.setDateFormat(fmt)
