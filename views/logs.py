from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)
from extra_qwidgets.fluent_widgets.pager import Pager
from qfluentwidgets import (
    TableView,
    ComboBox,
    FastCalendarPicker,
    PushButton,
    StrongBodyLabel,
    LineEdit,
)

from core.translator import Translator


class LogsView:
    def __init__(self):
        self.window = QDialog()
        self.window.setWindowTitle(Translator.translate("LogsWindow", "Logs"))
        self.window.setMinimumSize(800, 600)
        self.window.resize(1000, 800)
        self.window.setWindowIcon(QIcon("source/icons/window-icon.svg"))
        self.message_filter = LineEdit()
        self.message_filter.setPlaceholderText(
            Translator.translate("LogsWindow", "Message")
        )
        self.level_filter = ComboBox()
        self.date_filter = FastCalendarPicker()
        self.date_filter.setText(Translator.translate("LogsWindow", "Date"))
        self.date_filter.setDateFormat(Qt.DateFormat.TextDate)
        self.filter_button = PushButton()
        self.filter_button.setText(Translator.translate("LogsWindow", "Filter"))
        self.reset_filter_button = PushButton()
        self.reset_filter_button.setText(Translator.translate("LogsWindow", "Reset"))
        self.update_button = PushButton()
        self.update_button.setText(Translator.translate("LogsWindow", "Update"))
        self.logs_table = TableView()
        self.logs_table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self.pager = Pager()
        self.rows_count = StrongBodyLabel()
        self._setup_layout()

    def _setup_layout(self):
        filters_layout = QHBoxLayout()
        filters_layout.addWidget(self.message_filter)
        filters_layout.addWidget(self.level_filter)
        filters_layout.addWidget(self.date_filter)
        filters_layout.addWidget(self.filter_button)
        filters_layout.addWidget(self.reset_filter_button)
        filters_layout.addWidget(self.update_button)
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.rows_count)
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.pager)
        layout = QVBoxLayout()
        layout.addLayout(filters_layout)
        layout.addWidget(self.logs_table, 1)
        layout.addLayout(bottom_layout)
        self.window.setLayout(layout)
