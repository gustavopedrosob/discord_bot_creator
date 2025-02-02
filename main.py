import logging
import sys

from PySide6.QtCore import QTranslator
from PySide6.QtWidgets import QApplication
from core.config import instance as config
from interfaces.main.main import Main
import locale

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%x %X",
    )
    app = QApplication(sys.argv)
    lang = config.get("language")
    locale.setlocale(locale.LC_ALL, lang)
    translator = QTranslator()
    translator.load(f"translations/build/{lang}.qm")
    app.installTranslator(translator)
    window = Main()
    window.show()
    sys.exit(app.exec())
