import typing

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QListWidget,
    QLabel,
    QLineEdit,
    QListWidgetItem,
    QWidget,
    QComboBox,
)


class QListBox(QWidget):
    def __init__(self, title: str, line_edit: typing.Union[QLineEdit, QComboBox]):
        super().__init__()
        self.__layout = QVBoxLayout()
        self.__list = QListWidget()
        self.__label = QLabel(title)
        self.__line_edit = line_edit
        self.__layout.addWidget(self.__label)
        self.__layout.addWidget(self.__list)
        self.__layout.addWidget(self.__line_edit)
        if isinstance(self.__line_edit, QComboBox):
            self.__line_edit.lineEdit().returnPressed.connect(self.__add_item)
        else:
            self.__line_edit.returnPressed.connect(self.__add_item)
        self.setLayout(self.__layout)

    def __add_item(self):
        self.__list.addItem(QListWidgetItem(self.__line_edit.text()))
        self.__line_edit.clear()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            for item in self.__list.selectedItems():
                self.__list.takeItem(self.__list.row(item))
        else:
            super().keyPressEvent(event)

    def get_items_text(self) -> typing.List[str]:
        return [self.__list.item(i).text() for i in range(self.__list.count())]

    def add_item(self, item: str):
        self.__list.addItem(item)

    def add_items(self, items: typing.List[str]):
        self.__list.addItems(items)
