import typing

import qtawesome
from PySide6.QtCore import Qt, QCoreApplication, QSize
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QScrollArea,
)
from qfluentwidgets import ListWidget, TransparentToolButton, LineEdit, RoundMenu

translate = QCoreApplication.translate


class QListBox(QScrollArea):
    def __init__(self):
        super().__init__()
        self.__list = ListWidget()
        self.__list.setMinimumHeight(85)
        self.__add_button = TransparentToolButton()
        self.__add_button.setIcon(qtawesome.icon("fa6s.arrow-right"))
        self.__add_button.setIconSize(QSize(20, 20))
        self.__emote_button = TransparentToolButton()
        self.__emote_button.setIcon(qtawesome.icon("fa6s.face-smile"))
        self.__emote_button.setIconSize(QSize(20, 20))
        self.__line_edit = LineEdit()
        self.__horizontal_layout = QHBoxLayout()
        self.__horizontal_layout.addWidget(self.__line_edit)
        self.__horizontal_layout.addWidget(
            self.__add_button, alignment=Qt.AlignmentFlag.AlignTop
        )
        self.__horizontal_layout.addWidget(
            self.__emote_button, alignment=Qt.AlignmentFlag.AlignTop
        )
        self.__context_menu = RoundMenu()
        delete_action = QAction(translate("QListBox", "Remove"), self)
        delete_action.triggered.connect(self.__delete_selected_items)
        self.__context_menu.addAction(delete_action)
        self.__horizontal_layout.setStretch(0, True)
        self.setWidgetResizable(True)
        content_widget = QWidget()
        self.__layout = QVBoxLayout(content_widget)
        self.__layout.addWidget(self.__list)
        self.__layout.addLayout(self.__horizontal_layout)
        self.setWidget(content_widget)

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
        # noinspection PyArgumentList
        self.__list.addItem(*args)

    def add_items(self, items: typing.List[str]):
        self.__list.addItems(items)

    def reset(self):
        self.__line_edit.setText("")
        self.__list.clear()

    def entry_layout(self) -> QHBoxLayout:
        return self.__horizontal_layout

    def add_button(self) -> TransparentToolButton:
        return self.__add_button

    def emote_button(self) -> TransparentToolButton:
        return self.__emote_button

    def line_edit(self) -> LineEdit:
        return self.__line_edit

    def contextMenuEvent(self, event):
        if self.__is_selecting():
            self.__context_menu.exec(event.globalPos())

    def __delete_selected_items(self):
        for item in self.__list.selectedItems():
            self.__list.takeItem(self.__list.row(item))
