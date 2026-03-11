from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QComboBox,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QMessageBox,
)


class PrinterWidget(QWidget):
    def __init__(self, configs, printer, parent=None):
        super().__init__(parent)
        self.configs = configs
        self.printer = printer
        self.main_layout = QVBoxLayout()
        self.printer_list = QComboBox()
        self.populate()

        self.main_layout.addWidget(self.printer_list)

        self.set_printer_btn = QPushButton("Definir impressora padrão")
        self.set_printer_btn.setObjectName("primary")
        self.set_printer_btn.clicked.connect(self.set_default_printer)

        self.main_layout.addWidget(self.set_printer_btn)
        self.main_layout.setSpacing(15)
        self.setLayout(self.main_layout)

    def populate(self):
        """Populates the printer list with available system printers."""
        self.printer_list.addItems(self.printer.list_printers())
        saved_printer = self.configs.get("printer")
        if saved_printer:
            self.printer_list.setCurrentText(saved_printer)

    def selected_printer(self):
        """Returns the currently selected printer name."""
        return self.printer_list.currentText()

    def set_default_printer(self):
        """Saves the selected printer as the default one in configurations."""
        self.configs.set("printer", self.selected_printer())
        QMessageBox.information(
            self,
            "Sucesso",
            f"Impressora '{self.selected_printer()}' salva como padrão!",
        )
