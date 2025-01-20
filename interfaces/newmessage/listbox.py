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
    QTextEdit,
)

from interfaces.classes.colorresponsivebutton import QColorResponsiveButton


class QListBox(QWidget):
    def __init__(self, line_edit: typing.Union[QLineEdit, QComboBox, QTextEdit]):
        super().__init__()
        self.__list = QListWidget()
        self.__add_button = QColorResponsiveButton()
        self.__add_button.setIcon(QIcon("source/icons/plus-solid"))
        self.__add_button.setFlat(True)
        self.__line_edit = line_edit
        self.__horizontal_layout = QHBoxLayout()
        self.__horizontal_layout.addWidget(self.__line_edit)
        self.__horizontal_layout.addWidget(
            self.__add_button, alignment=Qt.AlignmentFlag.AlignTop
        )
        self.__horizontal_layout.setStretch(0, True)
        self.__layout = QVBoxLayout()
        self.__layout.addWidget(self.__list)
        self.__layout.addLayout(self.__horizontal_layout)
        self.setLayout(self.__layout)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            for item in self.__list.selectedItems():
                self.__list.takeItem(self.__list.row(item))
        else:
            super().keyPressEvent(event)

    def __is_selecting(self) -> bool:
        return bool(self.__list.selectedItems())

    def get_items_text(self) -> typing.List[str]:
        return [self.__list.item(i).text() for i in range(self.__list.count())]

    def get_items_userdata(self) -> typing.List[str]:
        return [
            self.__list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.__list.count())
        ]

    def add_item(self, *args):
        self.__list.addItem(*args)

    def add_items(self, items: typing.List[str]):
        self.__list.addItems(items)

    def entry_layout(self) -> QHBoxLayout:
        return self.__horizontal_layout

    def add_button(self) -> QColorResponsiveButton:
        return self.__add_button

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
