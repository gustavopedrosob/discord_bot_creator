from PySide6.QtWidgets import QGridLayout


class QRadioGroup:
    def __init__(self, label):
        self.layout = QGridLayout()
        self.label = label
        self.radios = {}
        self.current = None
        self.current_name = None

        self.layout.addWidget(self.label, 0, 0)
        self.layout.setContentsMargins(10, 10, 10, 10)

    def add_radio(self, name, radio):
        radio.clicked.connect(lambda r: self.radio_clicked(name, radio))
        self.layout.addWidget(radio, len(self.radios), 1)
        self.radios[name] = radio

    def radio_clicked(self, name, radio):
        if name == self.current_name:
            self.current.setChecked(False)
            self.current = None
            self.current_name = None
        else:
            self.current = radio
            self.current_name = name
            for r in self.radios.values():
                if r != radio:
                    r.setChecked(False)
            self.current.setChecked(True)
