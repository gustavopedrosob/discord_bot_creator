from PySide6.QtWidgets import QGridLayout, QWidget, QLabel


class QRadioGroup(QWidget):
    def __init__(self, label: QLabel):
        super().__init__()
        self.__layout = QGridLayout()
        self.__label = label
        self.__radios = {}
        self.__current = None
        self.__current_name = None
        self.__layout.addWidget(self.__label, 0, 0)
        self.setLayout(self.__layout)

    def add_radio(self, name: str, radio):
        radio.clicked.connect(lambda r: self.radio_clicked(name, radio))
        self.__layout.addWidget(radio, len(self.__radios), 1)
        self.__radios[name] = radio

    def radio_clicked(self, name: str, radio):
        if name == self.__current_name:
            self.__current.setChecked(False)
            self.__current = None
            self.__current_name = None
        else:
            self.__current = radio
            self.__current_name = name
            for r in self.__radios.values():
                if r != radio:
                    r.setChecked(False)
            self.__current.setChecked(True)

    def get_current_name(self):
        return self.__current_name

    def get_radio(self, name: str):
        return self.__radios[name]
