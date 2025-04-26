import typing

from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator, QAction
from PySide6.QtWidgets import (
    QScrollArea,
    QTableWidget,
    QComboBox,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QHeaderView,
    QLineEdit,
    QMenu,
)
from extra_qwidgets.utils import get_awesome_icon
from extra_qwidgets.widgets import QThemeResponsiveButton
from extra_qwidgets.widgets.theme_responsive_checkbutton import (
    QThemeResponsiveCheckButton,
)

from core.translator import Translator, FIELDS_TRANSLATIONS, OPERATORS_TRANSLATIONS
from interpreter.conditions import MessageConditionValidator
from models.condition import MessageCondition


class QConditionListbox(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.context_menu = QMenu(self)
        self.remove_action = QAction(self.tr("Remove"), self)
        self.field_combobox = QComboBox()
        self.operator_combobox = QComboBox()
        self.case_insensitive_checkbutton = QThemeResponsiveCheckButton()
        self.case_insensitive_checkbutton.setToolTip(self.tr("Case insensitive"))
        self.case_insensitive_checkbutton.setIcon(get_awesome_icon("font"))
        self.value_lineedit = QLineEdit()
        self.value_lineedit.setPlaceholderText(
            Translator.translate("QConditionListbox", "Value")
        )
        self.__add_button = QThemeResponsiveButton()
        self.__add_button.setIcon(get_awesome_icon("arrow-right"))
        self.__add_button.setFlat(True)
        self.setWidgetResizable(True)
        self.setup_binds()
        self.setup_layout()
        self.setup_context_menu()

    def open_context_menu(self, position):
        self.context_menu.exec(self.viewport().mapToGlobal(position))

    def on_remove(self):
        rows_to_delete = sorted(
            set(map(lambda item: item.row(), self.table.selectedItems()))
        )
        for row in reversed(list(rows_to_delete)):
            self.table.removeRow(row)

    def setup_layout(self):
        fields_layout = QHBoxLayout()
        fields_layout.addWidget(self.field_combobox, stretch=1)
        fields_layout.addWidget(self.operator_combobox, stretch=1)
        fields_layout.addWidget(self.case_insensitive_checkbutton)
        fields_layout.addWidget(self.value_lineedit, stretch=1)
        fields_layout.addWidget(self.__add_button)
        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.addWidget(self.table)
        main_layout.addLayout(fields_layout)
        self.setWidget(content_widget)

    def setup_context_menu(self):
        self.context_menu.addAction(self.remove_action)

    def setup_binds(self):
        self.__add_button.clicked.connect(self.on_add_condition)
        self.field_combobox.currentIndexChanged.connect(self.on_field_changed)
        self.table.customContextMenuRequested.connect(self.open_context_menu)
        self.remove_action.triggered.connect(self.on_remove)

    def on_field_changed(self):
        self.operator_combobox.clear()
        self.value_lineedit.clear()
        self._add_operators_options()
        self._setup_value_validator()

    def _add_fields_options(self):
        for data, text in FIELDS_TRANSLATIONS.items():
            self.field_combobox.addItem(text, data)

    def _is_current_field_str(self) -> bool:
        field_data = self.field_combobox.itemData(self.field_combobox.currentIndex())
        return field_data in MessageConditionValidator.STR_FIELDS

    def _add_operators_options(self):
        if self._is_current_field_str():
            operators = MessageConditionValidator.STR_OPERATORS
            self.case_insensitive_checkbutton.setDisabled(False)
        else:
            operators = MessageConditionValidator.INT_OPERATORS
            self.case_insensitive_checkbutton.setDisabled(True)
        for i in operators:
            self.operator_combobox.addItem(OPERATORS_TRANSLATIONS[i], i)

    def _setup_value_validator(self):
        if self._is_current_field_str():
            self.value_lineedit.setValidator(None)
        else:
            self.value_lineedit.setValidator(QIntValidator())

    def on_add_condition(self):
        field = self.field_combobox.currentText()
        field_data = self.field_combobox.itemData(self.field_combobox.currentIndex())
        operator = self.operator_combobox.currentText()
        operator_data = self.operator_combobox.itemData(
            self.operator_combobox.currentIndex()
        )
        if self._is_current_field_str():
            case_insensitive_data = self.case_insensitive_checkbutton.isChecked()
            case_insensitive = (
                self.tr("Yes") if case_insensitive_data else self.tr("No")
            )
        else:
            case_insensitive_data = None
            case_insensitive = "N/A"
        value = self.value_lineedit.text()
        self._add_condition(
            field,
            field_data,
            operator,
            operator_data,
            case_insensitive,
            case_insensitive_data,
            value,
        )

    def _add_condition(
        self,
        field: str,
        field_data: str,
        operator: str,
        operator_data: str,
        case_insensitive: str,
        case_insensitive_data: typing.Optional[bool],
        value: str,
    ):
        row = self.table.rowCount()
        self.table.insertRow(row)
        field_item = QTableWidgetItem(field)
        field_item.setData(Qt.ItemDataRole.UserRole, field_data)
        field_item.setFlags(field_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        operator_item = QTableWidgetItem(operator)
        operator_item.setData(Qt.ItemDataRole.UserRole, operator_data)
        operator_item.setFlags(operator_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        case_insensitive_item = QTableWidgetItem(case_insensitive)
        case_insensitive_item.setData(Qt.ItemDataRole.UserRole, case_insensitive_data)
        case_insensitive_item.setFlags(
            case_insensitive_item.flags() & ~Qt.ItemFlag.ItemIsEditable
        )
        value_item = QTableWidgetItem(value)
        value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 0, field_item)
        self.table.setItem(row, 1, operator_item)
        self.table.setItem(row, 2, case_insensitive_item)
        self.table.setItem(row, 3, value_item)

    def reset(self):
        self.table.clear()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            [
                self.tr("Field"),
                self.tr("Operator"),
                self.tr("Case insensitive"),
                self.tr("Value"),
            ]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setRowCount(0)
        self.field_combobox.clear()
        self.operator_combobox.clear()
        self.value_lineedit.clear()
        self._add_fields_options()

    def get_data(self, message_id: int) -> typing.List[MessageCondition]:
        conditions = []
        for row in range(self.table.rowCount()):
            field_item = self.table.item(row, 0)
            operator_item = self.table.item(row, 1)
            case_insensitive_item = self.table.item(row, 2)
            value_item = self.table.item(row, 3)
            if field_item and operator_item and value_item:
                field = field_item.data(Qt.ItemDataRole.UserRole)
                operator = operator_item.data(Qt.ItemDataRole.UserRole)
                value = value_item.text()
                case_insensitive = case_insensitive_item.data(Qt.ItemDataRole.UserRole)
                conditions.append(
                    MessageCondition(
                        message_id=message_id,
                        field=field,
                        operator=operator,
                        value=value,
                        case_insensitive=case_insensitive,
                    )
                )
        return conditions

    def load(self, conditions: typing.List[MessageCondition]):
        for condition in conditions:
            field_text = FIELDS_TRANSLATIONS[condition.field]
            operator_text = OPERATORS_TRANSLATIONS[condition.operator]
            value_text = condition.value
            if condition.case_insensitive is None:
                case_insensitive = "N/A"
                case_insensitive_data = None
            else:
                case_insensitive = (
                    self.tr("Yes") if condition.case_insensitive else self.tr("No")
                )
                case_insensitive_data = condition.case_insensitive
            self._add_condition(
                field_text,
                condition.field,
                operator_text,
                condition.operator,
                case_insensitive,
                case_insensitive_data,
                value_text,
            )
