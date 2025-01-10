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
        self.layout = QVBoxLayout()
        self.list = QListWidget()
        self.label = QLabel(title)
        self.line_edit = line_edit
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.list)
        self.layout.addWidget(self.line_edit)
        if isinstance(self.line_edit, QComboBox):
            self.line_edit.lineEdit().returnPressed.connect(self.add_item)
        else:
            self.line_edit.returnPressed.connect(self.add_item)
        self.setLayout(self.layout)

    def add_item(self):
        self.list.addItem(QListWidgetItem(self.line_edit.text()))
        self.line_edit.clear()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            for item in self.list.selectedItems():
                self.list.takeItem(self.list.row(item))
        else:
            super().keyPressEvent(event)

    def get_items_text(self):
        return [self.list.item(i).text() for i in range(self.list.count())]
