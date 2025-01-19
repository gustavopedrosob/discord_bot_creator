from PySide6.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget


class QResponsiveTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.adjust_height()
        self.textChanged.connect(self.adjust_height)

    def adjust_height(self):
        self.setFixedHeight(
            int(self.document().size().height())
            + self.contentsMargins().top()
            + self.contentsMargins().bottom()
        )

    def resizeEvent(self, e):
        self.adjust_height()
        super().resizeEvent(e)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QTextEdit Auto-ajustável")

        self.text_edit = QResponsiveTextEdit()
        self.text_edit.setPlaceholderText("Digite algo...")

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
