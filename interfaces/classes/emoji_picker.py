import typing

from PySide6.QtCore import QPoint, QCoreApplication, QSize, Signal
from PySide6.QtGui import QIcon, QFont, QAction, Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QScrollArea,
    QWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QGridLayout,
    QMenu,
    QPushButton,
    QDialog,
)
from emojis import emojis
from emojis.db import Emoji

from interfaces.classes.collapse_group import QCollapseGroup
from interfaces.classes.colorresponsivebutton import QColorResponsiveButton


class QEmojiButton(QPushButton):
    font = QFont()
    font.setPointSize(20)

    def __init__(self, emoji: Emoji):
        super().__init__(emoji.emoji)
        self.__favorite = False
        self.__emoji = emoji
        self.on_remove_favorite = QAction()
        self.on_remove_favorite.setText("Remove Favorite")
        self.on_favorite = QAction()
        self.on_favorite.setText("Favorite")
        self.setStyleSheet("padding: 0; background-color: transparent;")
        self.setFlat(True)
        self.setFont(self.font)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__context_menu_event)

    def favorite(self) -> bool:
        return self.__favorite

    def set_favorite(self, favorite: bool):
        self.__favorite = favorite

    def emoji(self) -> Emoji:
        return self.__emoji

    def has_in_aliases(self, emoji_alias: str) -> bool:
        for emoji_alias_2 in self.__emoji.aliases:
            if emoji_alias in emoji_alias_2:
                return True
        return False

    def __context_menu_event(self, position: QPoint):
        context_menu = QMenu()
        if self.favorite():
            context_menu.addAction(self.on_remove_favorite)
        else:
            context_menu.addAction(self.on_favorite)
        context_menu.exec(self.mapToGlobal(position))


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


class QEmojiPicker(QWidget):
    emoji_click = Signal(str)
    bottom_font = QFont()
    bottom_font.setBold(True)
    bottom_font.setPointSize(16)
    line_edit_font = QFont()
    line_edit_font.setPointSize(12)

    def __init__(self):
        super().__init__()
        self.__line_edit = QLineEdit()
        self.__line_edit.setFont(self.line_edit_font)
        self.__line_edit.setPlaceholderText(
            QCoreApplication.translate("QEmojiPicker", "Enter your favorite emoji")
        )
        self.__line_edit.textEdited.connect(self.__line_edited)
        self.__categories = {}
        self.__current_emoji_label = QLabel()
        self.__current_emoji_label.setFont(self.bottom_font)
        self.__menu_horizontal_layout = QHBoxLayout()
        self.__scroll_area = QScrollArea()
        self.__scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        self.__collapse_groups_layout = QVBoxLayout(content_widget)
        self.__scroll_area.setWidget(content_widget)
        self.__vertical_layout = QVBoxLayout()
        self.__vertical_layout.addLayout(self.__menu_horizontal_layout)
        self.__vertical_layout.addWidget(self.__line_edit)
        self.__vertical_layout.addWidget(self.__scroll_area)
        self.__vertical_layout.addWidget(self.__current_emoji_label)
        self.setLayout(self.__vertical_layout)
        self.add_category(
            "Favorite",
            QIcon("source/icons/star-solid.svg"),
            QCoreApplication.translate("QEmojiPicker", "Favorite"),
        )
        self.add_category(
            "Smileys & Emotion",
            QIcon("source/icons/face-smile-solid.svg"),
            QCoreApplication.translate("QEmojiPicker", "Smileys & Emotion"),
        )
        self.__insert_emojis("Smileys & Emotion")
        self.__insert_emojis("People & Body", "Smileys & Emotion")
        self.add_category(
            "Animals & Nature",
            QIcon("source/icons/leaf-solid.svg"),
            QCoreApplication.translate("QEmojiPicker", "Animals & Nature"),
        )
        self.__insert_emojis("Animals & Nature")
        self.add_category(
            "Food & Drink",
            QIcon("source/icons/bowl-food-solid.svg"),
            QCoreApplication.translate("QEmojiPicker", "Food & Drink"),
        )
        self.__insert_emojis("Food & Drink")
        self.add_category(
            "Activities",
            QIcon("source/icons/gamepad-solid.svg"),
            QCoreApplication.translate("QEmojiPicker", "Activities"),
        )
        self.__insert_emojis("Activities")
        self.add_category(
            "Travel & Places",
            QIcon("source/icons/bicycle-solid.svg"),
            QCoreApplication.translate("QEmojiPicker", "Travel & Places"),
        )
        self.__insert_emojis("Travel & Places")
        self.add_category(
            "Objects",
            QIcon("source/icons/lightbulb-solid.svg"),
            QCoreApplication.translate("QEmojiPicker", "Objects"),
        )
        self.__insert_emojis("Objects")
        self.add_category(
            "Symbols",
            QIcon("source/icons/heart-solid.svg"),
            QCoreApplication.translate("QEmojiPicker", "Symbols"),
        )
        self.__insert_emojis("Symbols")
        self.add_category(
            "Flags",
            QIcon("source/icons/flag-solid.svg"),
            QCoreApplication.translate("QEmojiPicker", "Flags"),
        )
        self.__insert_emojis("Flags")

    def add_category(self, category: str, icon: QIcon, title: str):
        shortcut_button = QColorResponsiveButton()
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
        self.__scroll_area.ensureWidgetVisible(collapse_group.header())

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
        emoji_button.on_favorite.triggered.connect(
            lambda event: self.add_favorite(emoji)
        )
        emoji_button.on_remove_favorite.triggered.connect(
            lambda event: self.remove_favorite(emoji)
        )
        emoji_button.pressed.connect(lambda: self.emoji_click.emit(emoji.emoji))

    def add_favorite(self, emoji: Emoji):
        emoji_button = self.emoji_button(emoji)
        if not emoji_button.favorite():
            favorite_emoji_grid = self.emoji_grid("Favorite")
            favorite_emoji_button = QEmojiButton(emoji_button.emoji())
            favorite_emoji_grid.add_emoji(favorite_emoji_button)
            self.__bind_emoji_button(favorite_emoji_button)
            favorite_emoji_button.set_favorite(True)
            emoji_button.set_favorite(True)
            favorite_emoji_grid.filter(self.__line_edit.text())

    def remove_favorite(self, emoji: Emoji):
        favorite_emoji_grid = self.emoji_grid("Favorite")
        favorite_emoji_button = favorite_emoji_grid.get_emoji(emoji)
        favorite_emoji_button.deleteLater()
        favorite_emoji_grid.update()
        emoji_button = self.emoji_button(emoji)
        if emoji_button:
            emoji_button.set_favorite(False)

    def emoji_button(self, emoji: Emoji) -> typing.Optional[QEmojiButton]:
        for category in self.__categories.keys():
            if category != "Favorite":
                emoji_grid = self.emoji_grid(category)
                return emoji_grid.get_emoji(emoji)

    def __mouse_enter_emoji(self, emoji: Emoji):
        aliases = " ".join(map(lambda alias: f":{alias}:", emoji.aliases))
        self.__current_emoji_label.setText(f"{emoji.emoji} {aliases}")

    def __line_edited(self):
        for category in self.__categories.keys():
            emoji_grid = self.emoji_grid(category)
            emoji_grid.filter(self.__line_edit.text())
            collapse_group = self.collapse_group(category)
            collapse_group.set_collapse(emoji_grid.all_hidden())

    def __mouse_leave_emoji(self):
        self.__current_emoji_label.clear()


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
