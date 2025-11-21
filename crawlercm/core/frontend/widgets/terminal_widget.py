# terminal_widget.py
from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtCore import Signal, QObject, Qt

class TerminalWidget(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMaximumBlockCount(5000)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-family: Consolas, monospace;
                font-size: 12px;
            }
        """)

    def write(self, text: str):
        self.appendPlainText(text)

    def flush(self):
        pass
