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
    def __init__(self, title: str, line_edit: typing.Union[QLineEdit, QComboBox]):
        super().__init__()
        self.__collapsed = False
        self.__widget = QWidget()
        self.__list = QListWidget()
        self.__collapse_button = QColorResponsiveButton()
        self.__collapse_button.setIcon(QIcon("source/icons/angle-down-solid.svg"))
        self.__collapse_button.setFlat(True)
        self.__collapse_button.clicked.connect(self.__collapse)
        self.__label = QLabel(title)
        self.__add_button = QColorResponsiveButton()
        self.__add_button.setIcon(QIcon("source/icons/plus-solid"))
        self.__add_button.clicked.connect(self.__add_item)
        self.__add_button.setFlat(True)
        self.__line_edit = line_edit
        self.__header_layout = QHBoxLayout()
        self.__header_layout.addWidget(self.__collapse_button)
        self.__header_layout.addWidget(self.__label)
        self.__header_layout.setStretch(1, True)
        self.__horizontal_layout = QHBoxLayout()
        self.__horizontal_layout.addWidget(self.__line_edit)
        self.__horizontal_layout.addWidget(self.__add_button)
        self.__horizontal_layout.setStretch(0, True)
        self.__widget_layout = QVBoxLayout()
        self.__widget_layout.addWidget(self.__list)
        self.__widget_layout.addLayout(self.__horizontal_layout)
        self.__widget.setLayout(self.__widget_layout)
        self.__layout = QVBoxLayout()
        self.__layout.addLayout(self.__header_layout)
        self.__layout.addWidget(self.__widget)
        self.setLayout(self.__layout)

    def __add_item(self):
        if isinstance(self.__line_edit, QComboBox):
            self.__list.addItem(QListWidgetItem(self.__line_edit.currentText()))
            self.__line_edit.clearEditText()
        else:
            self.__list.addItem(QListWidgetItem(self.__line_edit.text()))
            self.__line_edit.clear()

    def __collapse(self):
        if self.__collapsed:
            self.__widget.show()
            self.__collapse_button.setIcon(QIcon("source/icons/angle-down-solid.svg"))
        else:
            self.__widget.hide()
            self.__collapse_button.setIcon(QIcon("source/icons/angle-right-solid.svg"))
        self.__collapsed = not self.__collapsed

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
