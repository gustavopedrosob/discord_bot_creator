import qtawesome
from PySide6.QtCore import (
    Qt,
    QCoreApplication,
    QRegularExpression,
)
from PySide6.QtGui import (
    QIcon,
    QRegularExpressionValidator,
)
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QDialog,
    QLabel,
)
from extra_qwidgets.fluent_widgets.collapse_group import CollapseGroup
from extra_qwidgets.utils import colorize_icon
from extra_qwidgets.validators.emoji_validator import QEmojiValidator
from extra_qwidgets.widgets.checkboxes import QCheckBoxes
from qfluentwidgets import PushButton, CaptionLabel, LineEdit, SpinBox

from widgets.condition_listbox import QConditionListbox
from widgets.custom_button import ColoredPushButton
from widgets.custom_checkbox import QCustomCheckBox
from widgets.emoji_picker import QEmojiPickerPopup
from widgets.listbox import QListBox

translate = QCoreApplication.translate


class MessageView:
    def __init__(self):
        self.window = QDialog()
        self.window.setWindowFlags(
            self.window.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint
        )
        self.window.setWindowIcon(QIcon("source/icons/window-icon.svg"))
        self.window.setMinimumSize(800, 600)
        self.window.resize(1000, 800)
        self.window.setWindowTitle(translate("MessageWindow", "Message"))

        self.emoji_picker_popup = QEmojiPickerPopup()

        self.name_text = CaptionLabel()
        self.name_text.setText(translate("MessageWindow", "Name"))
        self.name_entry = LineEdit()
        self.name_entry.setToolTip(
            translate(
                "MessageWindow",
                "The name can include letters (with accents), numbers, and spaces. Example: 'John123'.",
            )
        )
        name_entry_validator = QRegularExpressionValidator(
            QRegularExpression(r"[A-zÀ-ú0-9 ]*")
        )
        self.name_entry.setMaxLength(40)
        self.name_entry.setValidator(name_entry_validator)
        self.listbox_conditions = QConditionListbox()
        self.listbox_reactions = QListBox()
        emoji_validator = QEmojiValidator()
        self.listbox_reactions.line_edit().setValidator(emoji_validator)
        self.listbox_replies = QListBox()
        self.collapse_group = CollapseGroup()
        self.collapse_group.addCollapse(
            translate("MessageWindow", "Conditions"), self.listbox_conditions
        )
        self.collapse_group.addCollapse(
            translate("MessageWindow", "Reactions"),
            self.listbox_reactions,
        )
        self.collapse_group.addCollapse(
            translate("MessageWindow", "Replies"), self.listbox_replies
        )

        self.group_pin_or_del = QCheckBoxes(
            QLabel(translate("MessageWindow", "Action"))
        )
        self.del_checkbox = QCustomCheckBox(
            "delete", translate("MessageWindow", "Delete")
        )
        self.group_pin_or_del.addCheckboxes(
            QCustomCheckBox("pin", translate("MessageWindow", "Pin")), self.del_checkbox
        )
        self.group_kick_or_ban = QCheckBoxes(
            QLabel(translate("MessageWindow", "Penalty"))
        )
        self.group_kick_or_ban.addCheckboxes(
            QCustomCheckBox("kick", translate("MessageWindow", "Kick")),
            QCustomCheckBox("ban", translate("MessageWindow", "Ban")),
        )
        self.group_where_reply = QCheckBoxes(
            QLabel(translate("MessageWindow", "Where reply"))
        )
        self.group_where_reply.addCheckboxes(
            QCustomCheckBox("group", translate("MessageWindow", "Group")),
            QCustomCheckBox("private", translate("MessageWindow", "Private")),
        )
        self.group_where_react = QCheckBoxes(
            QLabel(translate("MessageWindow", "Where react"))
        )
        self.author_checkbox = QCustomCheckBox(
            "author", translate("MessageWindow", "Author")
        )
        self.group_where_react.addCheckboxes(
            self.author_checkbox,
            QCustomCheckBox("bot", translate("MessageWindow", "Bot")),
        )
        self.delay_label = QLabel(translate("MessageWindow", "Delay"))
        self.delay = SpinBox()
        self.confirm = PushButton()
        self.confirm.setText(translate("MessageWindow", "Confirm"))
        self.confirm_and_save = ColoredPushButton("#3DCC61")
        self.confirm_and_save.setText(translate("MessageWindow", "Confirm and save"))
        self.confirm_and_save.setAutoDefault(False)
        self.confirm_and_save.setDefault(False)
        self.confirm_and_save.setIcon(
            colorize_icon(qtawesome.icon("fa6s.floppy-disk"), "#FFFFFF")
        )
        self.setup_layout()

    def setup_layout(self):
        left_layout = QVBoxLayout()
        mid_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        left_layout.addWidget(self.collapse_group)
        left_layout.setSpacing(0)
        left_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self.group_pin_or_del)
        right_layout.addWidget(self.group_kick_or_ban)
        right_layout.addWidget(self.group_where_reply)
        right_layout.addWidget(self.group_where_react)
        for widget in (
            self.delay_label,
            self.delay,
        ):
            right_layout.addWidget(widget)
        right_layout.addStretch()
        right_layout.addWidget(self.confirm)
        right_layout.addWidget(self.confirm_and_save)
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addLayout(left_layout)
        horizontal_layout.addLayout(mid_layout)
        horizontal_layout.addLayout(right_layout)
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.name_text)
        vertical_layout.addWidget(self.name_entry)
        vertical_layout.addLayout(horizontal_layout)
        self.window.setLayout(vertical_layout)
