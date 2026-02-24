from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QComboBox,
    QPushButton,
    QFileDialog,
    QMessageBox
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
        self.set_printer_btn.clicked.connect(self.set_default_printer)
        
        self.test_print_btn = QPushButton("Testar impressão (Texto RAW)")
        self.test_print_btn.clicked.connect(self.test_print)
        
        self.test_print_pdf_btn = QPushButton("Testar impressão (PDF)")
        self.test_print_pdf_btn.clicked.connect(self.test_print_pdf)

        self.main_layout.addWidget(self.set_printer_btn)
        self.main_layout.addWidget(self.test_print_btn)
        self.main_layout.addWidget(self.test_print_pdf_btn)
        
        self.setLayout(self.main_layout)

    def populate(self):
        self.printer_list.addItems(self.printer.list_printers())
        saved_printer = self.configs.get("printer")
        if saved_printer:
            self.printer_list.setCurrentText(saved_printer)

    def selected_printer(self):
        return self.printer_list.currentText()

    def set_default_printer(self):
        self.configs.set("printer", self.selected_printer())
        QMessageBox.information(self, "Sucesso", f"Impressora '{self.selected_printer()}' salva como padrão!")

    def test_print(self):
        try:
            self.printer.print_text(self.selected_printer(), "Teste de impressao RAW")
            QMessageBox.information(self, "Sucesso", "Comando de texto enviado com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro: {str(e)}")

    def test_print_pdf(self):
        default_printer = self.configs.get("printer")
        if not default_printer:
            default_printer = self.selected_printer()

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecione um arquivo PDF para imprimir", "", "PDF Files (*.pdf)"
        )

        if file_path:
            try:
                self.printer.print_pdf(default_printer, file_path)
                QMessageBox.information(self, "Sucesso", f"PDF enviado para a impressora:\n{default_printer}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao tentar imprimir o PDF:\n{str(e)}")