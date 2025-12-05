from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QComboBox,
    QPushButton,
)

from core.configs import Configs
from core.utils.printer import PrinterManager


class PrinterWidget(QWidget):
    def __init__(self, configs: Configs, printer: PrinterManager, parent=None):
        super().__init__(parent)
        self.configs = configs
        self.printer = printer
        self.main_layout = QVBoxLayout()
        self.printer_list = QComboBox()
        self.populate()

        self.main_layout.addWidget(self.printer_list)
        self.test_print_btn = QPushButton("Testar impressão")
        self.test_print_btn.clicked.connect(self.test_print)
        self.set_printer_btn = QPushButton("Definir impressora padrao")
        self.set_printer_btn.clicked.connect(self.set_default_printer)
        self.main_layout.addWidget(self.test_print_btn)
        self.main_layout.addWidget(self.set_printer_btn)
        self.setLayout(self.main_layout)

    def populate(self):
        self.printer_list.addItems(self.printer.list_printers())
        if self.configs.get("printer"):
            self.printer_list.setCurrentText(self.configs.get("printer"))
        self.main_layout.addWidget(self.printer_list)

    def selected_printer(self):
        return self.printer_list.currentText()

    def selected_printer_index(self):
        return self.printer_list.currentIndex()

    def set_default_printer(self):
        self.configs.set("printer", self.selected_printer())

    def test_print(self):
        self.printer.print_text(self.selected_printer(), "Teste")
