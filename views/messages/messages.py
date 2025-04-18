import typing

from PySide6.QtCore import (
    Qt,
    QCoreApplication,
    QRegularExpression,
    QMimeData,
)
from PySide6.QtGui import (
    QIcon,
    QRegularExpressionValidator,
    QKeyEvent,
    QValidator,
)
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QDialog,
    QLabel,
    QComboBox,
    QSpinBox,
    QLineEdit,
)
from extra_qwidgets.utils import get_awesome_icon, colorize_icon
from extra_qwidgets.widgets.checkboxes import QCheckBoxes
from extra_qwidgets.widgets.collapse_group import QCollapseGroup
from extra_qwidgets.widgets.color_button import QColorButton
from extra_qwidgets.widgets.emoji_picker.emoji_validator import QEmojiValidator
from extra_qwidgets.widgets.resposive_text_edit import QResponsiveTextEdit

from core.translator import Translator
from views.classes.custom_button import QCustomButton
from views.classes.custom_checkbox import QCustomCheckBox
from views.messages.listbox import QListBox

translate = QCoreApplication.translate


class QMessageTextEdit(QResponsiveTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMaximumHeight(400)
        self.__validator = None

    def validator(self) -> typing.Optional[QValidator]:
        return self.__validator

    def set_validator(self, validator: QValidator):
        self.__validator = validator

    def insertFromMimeData(self, source: QMimeData):
        if source.hasText():
            text = source.text()
            validator = self.validator()
            if validator and validator.validate(text, 0) not in (
                QValidator.State.Intermediate,
                QValidator.State.Acceptable,
            ):
                return
            mime_data = QMimeData()
            mime_data.setText(source.text())
            super().insertFromMimeData(mime_data)

    def keyPressEvent(self, e: QKeyEvent):
        if e.modifiers() == Qt.KeyboardModifier.NoModifier and e.key() not in (
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter,
            Qt.Key.Key_Backspace,
        ):
            text = self.toPlainText() + e.text()
            validator = self.validator()
            if validator and validator.validate(text, 0) not in (
                QValidator.State.Intermediate,
                QValidator.State.Acceptable,
            ):
                return
            super().keyPressEvent(e)
        else:
            super().keyPressEvent(e)


class MessageView:
    translated_conditions = {
        "expected message": Translator.translate("Conditions", "expected message"),
        "not expected message": Translator.translate("Conditions", "not expected message"),
        "mention bot": Translator.translate("Conditions", "mention bot"),
        "not mention bot": Translator.translate("Conditions", "not mention bot"),
        "mention someone": Translator.translate("Conditions", "mention someone"),
        "not mention someone": Translator.translate("Conditions", "not mention someone"),
        "mention everyone": Translator.translate("Conditions", "mention everyone"),
        "not mention everyone": Translator.translate("Conditions", "not mention everyone"),
        "author is bot": Translator.translate("Conditions", "author is bot"),
        "not author is bot": Translator.translate("Conditions", "not author is bot"),
        "number in message": Translator.translate("Conditions", "number in message"),
        "not number in message": Translator.translate("Conditions", "not number in message"),
        "symbols in message": Translator.translate("Conditions", "symbols in message"),
        "not symbols in message": Translator.translate("Conditions", "not symbols in message"),
        "emojis in message": Translator.translate("Conditions", "emojis in message"),
        "not emojis in message": Translator.translate("Conditions", "not emojis in message"),
    }

    def __init__(self):
        self.window = QDialog()
        self.window.setWindowFlags(
            self.window.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint
        )
        self.window.setWindowIcon(QIcon("source/icons/window-icon.svg"))
        self.window.setMinimumSize(800, 600)
        self.window.resize(1000, 800)
        self.window.setWindowTitle(translate("MessageWindow", "Message"))

        self.emoji_picker_popup = None

        self.name_text = QLabel(translate("MessageWindow", "Name"))
        self.name_entry = QLineEdit()
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
        self.conditions_combobox = QComboBox()
        for condition, translated_condition in self.translated_conditions.items():
            self.conditions_combobox.addItem(translated_condition, condition)

        self.listbox_conditions = QListBox(self.conditions_combobox)
        self.collapse_conditions = QCollapseGroup(
            translate("MessageWindow", "Conditions"),
            self.listbox_conditions,
        )
        self.collapse_conditions.setContentsMargins(0, 0, 0, 0)
        emoji_validator = QEmojiValidator()
        self.reactions_line_edit = QMessageTextEdit()
        self.reactions_line_edit.set_validator(emoji_validator)
        self.listbox_reactions = QListBox(self.reactions_line_edit)
        self.collapse_reactions = QCollapseGroup(
            translate("MessageWindow", "Reactions"),
            self.listbox_reactions,
        )
        self.collapse_reactions.setContentsMargins(0, 0, 0, 0)
        self.messages_line_edit = QMessageTextEdit()
        self.listbox_messages = QListBox(self.messages_line_edit)
        self.collapse_messages = QCollapseGroup(
            translate("MessageWindow", "Messages"), self.listbox_messages
        )
        self.collapse_messages.setContentsMargins(0, 0, 0, 0)
        self.replies_line_edit = QMessageTextEdit()
        self.listbox_replies = QListBox(self.replies_line_edit)
        self.collapse_replies = QCollapseGroup(
            translate("MessageWindow", "Replies"), self.listbox_replies
        )
        self.collapse_replies.setContentsMargins(0, 0, 0, 0)

        self.group_pin_or_del = QCheckBoxes(
            QLabel(translate("MessageWindow", "Action"))
        )
        self.del_checkbox = QCustomCheckBox("delete", translate("MessageWindow", "Delete"))
        self.group_pin_or_del.add_checkboxes(
            QCustomCheckBox("pin", translate("MessageWindow", "Pin")), self.del_checkbox
        )
        self.group_kick_or_ban = QCheckBoxes(
            QLabel(translate("MessageWindow", "Penalty"))
        )
        self.group_kick_or_ban.add_checkboxes(
            QCustomCheckBox("kick", translate("MessageWindow", "Kick")),
            QCustomCheckBox("ban", translate("MessageWindow", "Ban")),
        )
        self.group_where_reply = QCheckBoxes(
            QLabel(translate("MessageWindow", "Where reply"))
        )
        self.group_where_reply.add_checkboxes(
            QCustomCheckBox("group", translate("MessageWindow", "Group")),
            QCustomCheckBox("private", translate("MessageWindow", "Private")),
        )
        self.group_where_react = QCheckBoxes(
            QLabel(translate("MessageWindow", "Where react"))
        )
        self.author_checkbox = QCustomCheckBox(
            "author", translate("MessageWindow", "Author")
        )
        self.group_where_react.add_checkboxes(
            self.author_checkbox, QCustomCheckBox("bot", translate("MessageWindow", "Bot"))
        )
        self.delay_label = QLabel(translate("MessageWindow", "Delay"))
        self.delay = QSpinBox()
        self.confirm = QCustomButton(translate("MessageWindow", "Confirm"))
        self.confirm_and_save = QColorButton(
            translate("MessageWindow", "Confirm and save"), "#3DCC61"
        )
        self.confirm_and_save.setAutoDefault(False)
        self.confirm_and_save.setDefault(False)
        self.confirm_and_save.setIcon(
            colorize_icon(get_awesome_icon("floppy-disk"), "#FFFFFF")
        )
        self.setup_layout()

    def setup_layout(self):
        left_layout = QVBoxLayout()
        mid_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        for widget in (
            self.collapse_conditions,
            self.collapse_reactions,
            self.collapse_messages,
            self.collapse_replies,
        ):
            left_layout.addWidget(widget)
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
