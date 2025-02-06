import typing
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QSize, Signal, QTimer
from PySide6.QtGui import QIcon, QFont, Qt, QPixmap, QImage
from PySide6.QtWidgets import (
    QVBoxLayout,
    QScrollArea,
    QWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QGridLayout,
    QPushButton,
    QDialog,
)
from emojis import emojis
from emojis.db import Emoji

from interfaces.classes.collapse_group import QCollapseGroup
from interfaces.classes.color_responsive_button import QColorResponsiveButton
from interfaces.classes.custom_button import QCustomButton

translate = QCoreApplication.translate


class EmojiUtils:
    @staticmethod
    def _to_code_point(surrogate_pair_str, delimiter="-"):
        # Convert the string into a list of UTF-16 code units
        code_units = [ord(char) for char in surrogate_pair_str]

        # Process the code units in pairs (high surrogate + low surrogate)
        code_points = []
        i = 0
        while i < len(code_units):
            high_surrogate = code_units[i]
            low_surrogate = code_units[i + 1] if i + 1 < len(code_units) else None

            # Check if the current pair is a valid surrogate pair
            if 0xD800 <= high_surrogate <= 0xDBFF and 0xDC00 <= low_surrogate <= 0xDFFF:
                # Calculate the code point
                code_point = (
                    ((high_surrogate - 0xD800) << 10)
                    + (low_surrogate - 0xDC00)
                    + 0x10000
                )
                code_points.append(hex(code_point)[2:])  # Remove the '0x' prefix
                i += 2  # Move to the next pair
            else:
                # If not a surrogate pair, treat it as a regular code point
                code_points.append(hex(high_surrogate)[2:])
                i += 1

        # Join the code points with the specified delimiter
        return delimiter.join(code_points)

    @classmethod
    def _get_icon_path(cls, emoji: Emoji) -> str:
        file_name = cls._to_code_point(emoji.emoji)
        path = Path(f"source/emojis/{file_name}.png")
        if path.exists():
            return str(path)
        else:
            file_name = "-".join(file_name.split("-")[:-1])
            return f"source/emojis/{file_name}.png"


class QEmojiButton(QCustomButton, EmojiUtils):
    def __init__(self, emoji: Emoji):
        super().__init__()
        self.__emoji = emoji
        self.setIcon(QIcon(self._get_icon_path(emoji)))
        self.setFixedSize(QSize(40, 40))
        self.setIconSize(QSize(36, 36))
        self.setStyleSheet("padding: 0; background-color: transparent;")
        self.setFlat(True)

    def emoji(self) -> Emoji:
        return self.__emoji

    def has_in_aliases(self, emoji_alias: str) -> bool:
        return any(
            emoji_alias in emoji_alias_2 for emoji_alias_2 in self.__emoji.aliases
        )


class QEmojiGrid(QWidget):
    def __init__(self):
        super().__init__()
        self.__hidden_emojis = []
        self.__grid_layout = QGridLayout()
        self.__grid_layout.setSpacing(0)
        self.setLayout(self.__grid_layout)

    def add_emoji(self, emoji: QEmojiButton):
        self.__grid_layout.addWidget(
            emoji, *self.__next_position(self.layout().count())
        )

    def get_emoji(self, emoji: Emoji) -> typing.Optional[QEmojiButton]:
        for emoji_2 in self.emojis():
            if emoji_2.emoji() == emoji:
                return emoji_2

    def emojis(self) -> list[QEmojiButton]:
        return list(
            filter(
                lambda emoji_button: isinstance(emoji_button, QEmojiButton),
                self.children(),
            )
        )

    def all_hidden(self) -> bool:
        return len(self.__hidden_emojis) == len(self.emojis())

    def filter(self, emoji_alias: str):
        removed = 0
        all_emojis = self.emojis()
        for index, emoji_button in enumerate(all_emojis):
            if emoji_button.has_in_aliases(emoji_alias):
                if emoji_button in self.__hidden_emojis:
                    self.__hidden_emojis.remove(emoji_button)
                    emoji_button.show()
                else:
                    self.__grid_layout.removeWidget(emoji_button)
                position = self.__next_position(index - removed)
                self.__grid_layout.addWidget(emoji_button, *position)
            else:
                if emoji_button not in self.__hidden_emojis:
                    self.__grid_layout.removeWidget(emoji_button)
                    emoji_button.hide()
                    self.__hidden_emojis.append(emoji_button)
                removed += 1
        self.__grid_layout.update()
        self.update()

    @staticmethod
    def __next_position(index: int) -> tuple[int, int]:
        return index // 9, index % 9


class QEmojiPicker(QWidget, EmojiUtils):
    emoji_click = Signal(str)
    aliases_emoji_font = QFont()
    aliases_emoji_font.setBold(True)
    aliases_emoji_font.setPointSize(13)
    line_edit_font = QFont()
    line_edit_font.setPointSize(12)

    def __init__(self):
        super().__init__()
        self.__line_edit = QLineEdit()
        self.__line_edit.setFont(self.line_edit_font)
        self.__line_edit.setPlaceholderText(
            translate("QEmojiPicker", "Enter your favorite emoji")
        )
        self.__line_edit.textEdited.connect(self.__line_edited)
        self.__categories = {}
        self.__emoji_label = QLabel()
        self.__emoji_label.setFixedSize(QSize(32, 32))
        self.__emoji_label.setScaledContents(True)
        self.__aliases_emoji_label = QLabel()
        self.__aliases_emoji_label.setFont(self.aliases_emoji_font)
        self.__menu_horizontal_layout = QHBoxLayout()
        self.__scroll_area = QScrollArea()
        self.__scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        self.__collapse_groups_layout = QVBoxLayout(content_widget)
        self.__scroll_area.setWidget(content_widget)
        self.__emoji_layout = QHBoxLayout()
        self.__emoji_layout.addWidget(self.__emoji_label)
        self.__emoji_layout.addWidget(self.__aliases_emoji_label)
        self.__emoji_layout.setStretch(1, True)
        self.__vertical_layout = QVBoxLayout()
        self.__vertical_layout.addLayout(self.__menu_horizontal_layout)
        self.__vertical_layout.addWidget(self.__line_edit)
        self.__vertical_layout.addWidget(self.__scroll_area)
        self.__vertical_layout.addLayout(self.__emoji_layout)
        self.setLayout(self.__vertical_layout)
        self.add_category(
            "Smileys & Emotion",
            QIcon("source/icons/face-smile-solid.svg"),
            translate("QEmojiPicker", "Smileys & Emotion"),
        )
        self.__insert_emojis("Smileys & Emotion")
        self.__insert_emojis("People & Body", "Smileys & Emotion")
        self.add_category(
            "Animals & Nature",
            QIcon("source/icons/leaf-solid.svg"),
            translate("QEmojiPicker", "Animals & Nature"),
        )
        self.__insert_emojis("Animals & Nature")
        self.add_category(
            "Food & Drink",
            QIcon("source/icons/bowl-food-solid.svg"),
            translate("QEmojiPicker", "Food & Drink"),
        )
        self.__insert_emojis("Food & Drink")
        self.add_category(
            "Activities",
            QIcon("source/icons/gamepad-solid.svg"),
            translate("QEmojiPicker", "Activities"),
        )
        self.__insert_emojis("Activities")
        self.add_category(
            "Travel & Places",
            QIcon("source/icons/bicycle-solid.svg"),
            translate("QEmojiPicker", "Travel & Places"),
        )
        self.__insert_emojis("Travel & Places")
        self.add_category(
            "Objects",
            QIcon("source/icons/lightbulb-solid.svg"),
            translate("QEmojiPicker", "Objects"),
        )
        self.__insert_emojis("Objects")
        self.add_category(
            "Symbols",
            QIcon("source/icons/heart-solid.svg"),
            translate("QEmojiPicker", "Symbols"),
        )
        self.__insert_emojis("Symbols")
        self.add_category(
            "Flags",
            QIcon("source/icons/flag-solid.svg"),
            translate("QEmojiPicker", "Flags"),
        )
        self.__insert_emojis("Flags")

    def add_category(self, category: str, icon: QIcon, title: str):
        shortcut_button = QColorResponsiveButton()
        shortcut_button.setFixedSize(QSize(30, 30))
        shortcut_button.setIconSize(QSize(22, 22))
        shortcut_button.setFlat(True)
        shortcut_button.setIcon(icon)
        shortcut_button.clicked.connect(lambda: self.__collapse_all_but(category))
        shortcut_button.clicked.connect(lambda: self.__scroll_to_category(category))
        self.__menu_horizontal_layout.addWidget(shortcut_button)
        collapse_group = QCollapseGroup(title, QEmojiGrid())
        self.__categories[category] = {
            "shortcut": shortcut_button,
            "group": collapse_group,
        }
        self.__collapse_groups_layout.addWidget(collapse_group)

    def __collapse_all_but(self, category: str):
        for category_2 in self.__categories.keys():
            if category_2 != category:
                self.collapse_group(category_2).set_collapse(True)
        self.collapse_group(category).set_collapse(False)

    def __scroll_to_category(self, category: str):
        collapse_group = self.collapse_group(category)
        self.__scroll_area.verticalScrollBar().setValue(collapse_group.y())

    def collapse_group(self, category: str) -> QCollapseGroup:
        return self.__categories[category]["group"]

    def emoji_grid(self, category: str) -> QEmojiGrid:
        return self.__categories[category]["group"].widget()

    def shortcut(self, category: str) -> QColorResponsiveButton:
        return self.__categories[category]["shortcut"]

    def __insert_emojis(self, category: str, to: typing.Optional[str] = None):
        if to is None:
            to = category
        emoji_grid = self.emoji_grid(to)
        for emoji in emojis.db.get_emojis_by_category(category):
            emoji_button = QEmojiButton(emoji)
            self.__bind_emoji_button(emoji_button)
            emoji_grid.add_emoji(emoji_button)

    def __bind_emoji_button(self, emoji_button: QEmojiButton):
        emoji = emoji_button.emoji()
        emoji_button.enterEvent = lambda event: self.__mouse_enter_emoji(emoji)
        emoji_button.leaveEvent = lambda event: self.__mouse_leave_emoji()
        emoji_button.pressed.connect(lambda: self.emoji_click.emit(emoji.emoji))

    def emoji_button(self, emoji: Emoji) -> typing.Optional[QEmojiButton]:
        for category in self.__categories.keys():
            emoji_grid = self.emoji_grid(category)
            return emoji_grid.get_emoji(emoji)

    def __mouse_enter_emoji(self, emoji: Emoji):
        aliases = " ".join(map(lambda alias: f":{alias}:", emoji.aliases))
        self.__emoji_label.setPixmap(QPixmap(self._get_icon_path(emoji)))
        self.__aliases_emoji_label.setText(aliases)

    def __line_edited(self):
        for category in self.__categories.keys():
            emoji_grid = self.emoji_grid(category)
            emoji_grid.filter(self.__line_edit.text())
            collapse_group = self.collapse_group(category)
            all_hidden = emoji_grid.all_hidden()
            collapse_group.set_collapse(all_hidden)
            collapse_group.setHidden(all_hidden)

    def __mouse_leave_emoji(self):
        self.__emoji_label.clear()
        self.__aliases_emoji_label.clear()

    def reset(self):
        self.__line_edit.clear()
        self.__line_edited()
        self.__scroll_area.verticalScrollBar().setValue(0)


class QEmojiPickerPopup(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setFixedSize(QSize(500, 500))
        self.__emoji_picker = QEmojiPicker()
        layout = QVBoxLayout()
        layout.addWidget(self.__emoji_picker)
        self.setLayout(layout)

    def emoji_picker(self):
        return self.__emoji_picker
