from PySide6.QtGui import QColor

TEXT = "text"
PRIMARY = "primary"
SECONDARY = "secondary"
SUCCESS = "success"
DANGER = "danger"
WARNING = "warning"
INFO = "info"


LIGHT_THEME = {
    TEXT: QColor("#000000"),
    PRIMARY: QColor("#095AD1"),
    SECONDARY: QColor("#5A6269"),
    SUCCESS: QColor("#136F44"),
    DANGER: QColor("#B62A37"),
    WARNING: QColor("#8B6702"),
    INFO: QColor("#04778F"),
}

DARK_THEME = {
    TEXT: QColor("#ffffff"),
    PRIMARY: QColor("#0D6EFD"),
    SECONDARY: QColor("#929EA8"),
    SUCCESS: QColor("#24B270"),
    DANGER: QColor("#FC6E77"),
    WARNING: QColor("#FFC107"),
    INFO: QColor("#0DCAF0"),
}
