import typing

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QVBoxLayout,
    QListWidget,
    QLabel,
    QLineEdit,
    QListWidgetItem,
    QComboBox,
    QMenu,
    QHBoxLayout,
    QWidget,
)

from interfaces.classes.colorresponsivebutton import QColorResponsiveButton


class QListBox(QWidget):
    def __init__(self, line_edit: typing.Union[QLineEdit, QComboBox]):
        super().__init__()
        self.__list = QListWidget()
        self.__add_button = QColorResponsiveButton()
        self.__add_button.setIcon(QIcon("source/icons/plus-solid"))
        self.__add_button.clicked.connect(self.__add_item)
        self.__add_button.setFlat(True)
        self.__line_edit = line_edit
        self.__horizontal_layout = QHBoxLayout()
        self.__horizontal_layout.addWidget(self.__line_edit)
        self.__horizontal_layout.addWidget(self.__add_button)
        self.__horizontal_layout.setStretch(0, True)
        self.__layout = QVBoxLayout()
        self.__layout.addWidget(self.__list)
        self.__layout.addLayout(self.__horizontal_layout)
        self.setLayout(self.__layout)

    def __add_item(self):
        if isinstance(self.__line_edit, QComboBox):
            text = self.__line_edit.currentText()
            if text:
                self.__list.addItem(QListWidgetItem(text))
                self.__line_edit.clearEditText()
        else:
            text = self.__line_edit.text()
            if text:
                self.__list.addItem(QListWidgetItem(text))
                self.__line_edit.clear()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            for item in self.__list.selectedItems():
                self.__list.takeItem(self.__list.row(item))
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.__add_item()
        else:
            super().keyPressEvent(event)

    def __is_selecting(self) -> bool:
        return bool(self.__list.selectedItems())

    def get_items_text(self) -> typing.List[str]:
        return [self.__list.item(i).text() for i in range(self.__list.count())]

    def add_item(self, item: str):
        self.__list.addItem(item)

    def add_items(self, items: typing.List[str]):
        self.__list.addItems(items)

    def contextMenuEvent(self, event):
        if self.__is_selecting():
            context_menu = QMenu(self)
            delete_action = QAction("Remover", self)
            delete_action.triggered.connect(self.__delete_selected_items)
            context_menu.addAction(delete_action)
            context_menu.exec(event.globalPos())

    def __delete_selected_items(self):
        for item in self.__list.selectedItems():
            self.__list.takeItem(self.__list.row(item))
