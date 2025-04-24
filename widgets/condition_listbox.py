import typing

from PySide6.QtCore import Qt
from PySide6.QtGui import QValidator, QIntValidator, QAction
from PySide6.QtWidgets import QScrollArea, QTableWidget, QComboBox, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QWidget, \
    QHeaderView, QLineEdit, QMenu
from extra_qwidgets.utils import get_awesome_icon
from extra_qwidgets.widgets import QThemeResponsiveButton

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
        self.value_lineedit = QLineEdit()
        self.value_lineedit.setPlaceholderText(Translator.translate("QConditionListbox", "Value"))
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
        rows_to_delete = sorted(set(map(lambda item: item.row(), self.table.selectedItems())))
        for row in reversed(list(rows_to_delete)):
            self.table.removeRow(row)

    def setup_layout(self):
        fields_layout = QHBoxLayout()
        fields_layout.addWidget(self.field_combobox, stretch=1)
        fields_layout.addWidget(self.operator_combobox, stretch=1)
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

    def _add_operators_options(self):
        field_data = self.field_combobox.itemData(self.field_combobox.currentIndex())
        if field_data in MessageConditionValidator.STR_FIELDS:
            operators = MessageConditionValidator.STR_OPERATORS
        else:
            operators = MessageConditionValidator.INT_OPERATORS
        for i in operators:
            self.operator_combobox.addItem(OPERATORS_TRANSLATIONS[i], i)

    def _setup_value_validator(self):
        field_data = self.field_combobox.itemData(self.field_combobox.currentIndex())
        if field_data in MessageConditionValidator.STR_FIELDS:
            self.value_lineedit.setValidator(None)
        else:
            self.value_lineedit.setValidator(QIntValidator())

    def on_add_condition(self):
        field = self.field_combobox.currentText()
        field_data = self.field_combobox.itemData(self.field_combobox.currentIndex())
        operator = self.operator_combobox.currentText()
        operator_data = self.operator_combobox.itemData(self.operator_combobox.currentIndex())
        value = self.value_lineedit.text()
        self._add_condition(field, field_data, operator, operator_data, value)

    def _add_condition(self, field: str, field_data: str, operator: str, operator_data: str, value: str):
        row = self.table.rowCount()
        self.table.insertRow(row)
        field_item = QTableWidgetItem(field)
        field_item.setData(Qt.ItemDataRole.UserRole, field_data)
        field_item.setFlags(field_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        operator_item = QTableWidgetItem(operator)
        operator_item.setData(Qt.ItemDataRole.UserRole, operator_data)
        operator_item.setFlags(operator_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        value_item = QTableWidgetItem(value)
        value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 0, field_item)
        self.table.setItem(row, 1, operator_item)
        self.table.setItem(row, 2, value_item)

    def reset(self):
        self.table.clear()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([self.tr("Field"), self.tr("Operator"), self.tr("Value")])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
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
            value_item = self.table.item(row, 2)
            if field_item and operator_item and value_item:
                field = field_item.data(Qt.ItemDataRole.UserRole)
                operator = operator_item.data(Qt.ItemDataRole.UserRole)
                value = value_item.text()
                conditions.append(MessageCondition(message_id=message_id, field=field, operator=operator, value=value))
        return conditions

    def load(self, conditions: typing.List[MessageCondition]):
        for condition in conditions:
            field_text = FIELDS_TRANSLATIONS[condition.field]
            operator_text = OPERATORS_TRANSLATIONS[condition.operator]
            value_text = condition.value
            self._add_condition(field_text, condition.field, operator_text, condition.operator, value_text)
