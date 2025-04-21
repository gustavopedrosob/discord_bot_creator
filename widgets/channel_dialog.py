import typing

from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel, QIcon
from PySide6.QtWidgets import (
    QDialog,
    QTreeView,
    QFormLayout,
    QPushButton,
    QHBoxLayout,
    QSpacerItem,
    QSizePolicy,
)
from discord import Guild

from widgets.text_channel_item import TextChannelItem
from widgets.voice_channel_item import VoiceChannelItem

translate = QCoreApplication.translate


class ChannelDialog(QDialog):
    def __init__(self, group: typing.Optional[Guild] = None):
        super().__init__()
        self.setWindowTitle(self.tr("Select a channel"))
        self.setWindowIcon(QIcon("source/icons/window-icon.svg"))
        self.setMinimumSize(400, 650)

        self.text_item = QStandardItem(translate("GroupWindow", "Text channels"))
        self.text_item.setEditable(False)
        self.text_item.setSelectable(False)
        self.voice_item = QStandardItem(translate("GroupWindow", "Voice channels"))
        self.voice_item.setEditable(False)
        self.voice_item.setSelectable(False)

        self.channels_model = QStandardItemModel()
        self.channels_treeview = QTreeView()
        self.channels_treeview.setModel(self.channels_model)

        self.accept_button = QPushButton(self.tr("Select"))
        self.accept_button.clicked.connect(self.on_accept_pressed)
        self.cancel_button = QPushButton(self.tr("Cancel"))
        self.cancel_button.clicked.connect(self.reject)
        self.setup_layout()
        if group:
            self.update_channels(group)

    def setup_layout(self):
        main_layout = QFormLayout()
        main_layout.addRow(self.channels_treeview)
        buttons_layout = QHBoxLayout()
        buttons_layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        )
        buttons_layout.addWidget(
            self.cancel_button, alignment=Qt.AlignmentFlag.AlignRight
        )
        buttons_layout.addWidget(
            self.accept_button, alignment=Qt.AlignmentFlag.AlignRight
        )

        main_layout.addItem(buttons_layout)
        self.setLayout(main_layout)

    def get_selected_channel_id(self) -> typing.Optional[int]:
        selection = self.channels_treeview.selectedIndexes()
        if len(selection) == 1:
            selected_channel: QStandardItem = self.channels_model.itemFromIndex(
                selection[0]
            )
            return selected_channel.data(Qt.ItemDataRole.UserRole)
        return None

    def on_accept_pressed(self):
        channel_id = self.get_selected_channel_id()
        if channel_id:
            self.accept()

    def update_channels(self, group: Guild):
        self.channels_model.clear()
        self.channels_model.setHorizontalHeaderLabels(
            [translate("GroupWindow", "Channels")]
        )
        self.text_item.appendRows([TextChannelItem(tc) for tc in group.text_channels])
        self.channels_model.appendRow(self.text_item)
        self.voice_item.appendRows(
            [VoiceChannelItem(vc) for vc in group.voice_channels]
        )
        self.channels_model.appendRow(self.voice_item)
        self.channels_treeview.expandAll()

    def reset(self):
        self.text_item.removeRows(0, self.text_item.rowCount())
        self.voice_item.removeRows(0, self.voice_item.rowCount())
