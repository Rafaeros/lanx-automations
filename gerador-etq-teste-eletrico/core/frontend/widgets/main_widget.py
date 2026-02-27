import os
from datetime import datetime as dt

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QMessageBox

from core.configs import Configs
from core.frontend.widgets.search_production_order_widget import (
    SearchProductOrderWidget,
)
from core.frontend.widgets.select_operator_widget import SelectOperatorWidget
from core.utils.labels import generate_labels
from core.utils.printer import PrinterManager


class MainWidget(QWidget):
    def __init__(self, configs: Configs, printer_manager: PrinterManager, parent=None):
        super().__init__(parent)
        self.configs = configs
        self.printer = printer_manager

        self.main_layout = QVBoxLayout()

        self.operator_list_widget = SelectOperatorWidget(self.configs)
        self.search_product_order_widget = SearchProductOrderWidget(self.configs)

        self.main_layout.addWidget(self.operator_list_widget)
        self.main_layout.addWidget(self.search_product_order_widget)

        self.print_button = QPushButton("Imprimir Etiqueta")
        self.print_button.clicked.connect(self.print_label)
        self.main_layout.addWidget(self.print_button)

        self.main_layout.addStretch(1)
        self.setLayout(self.main_layout)

    def print_label(self):
        printer_name = self.configs.get("printer")
        if not printer_name:
            QMessageBox.warning(
                self,
                "Aviso",
                "Nenhuma impressora padrão configurada.\nVá nas configurações e defina uma impressora antes de imprimir.",
            )
            return
        current_date = dt.now().strftime("%d/%m/%Y-%H:%M")
        date_part, time_part = current_date.split("-")

        try:
            quantity = int(self.search_product_order_widget.quantity_input.text())

            file_path = generate_labels(
                self.search_product_order_widget.search_input.text(),
                self.search_product_order_widget.product_input.text(),
                self.search_product_order_widget.client_input.text(),
                self.operator_list_widget.operator_combo_box.currentText(),
                self.search_product_order_widget.description_input.text(),
                self.search_product_order_widget.client_code_input.text(),
                date_part,
                time_part,
                quantity=quantity,
            )

            if not file_path or not os.path.exists(file_path):
                raise FileNotFoundError(
                    "O arquivo da etiqueta não pôde ser encontrado após a geração."
                )

            self.printer.print_label(printer_name, file_path, quantity)

            self.search_product_order_widget.search_input.setText("")
            self.search_product_order_widget.product_input.setText("")
            self.search_product_order_widget.client_input.setText("")
            self.search_product_order_widget.description_input.setText("")
            self.search_product_order_widget.client_code_input.setText("")
            self.search_product_order_widget.quantity_input.setText("")
            QMessageBox.information(self, "Sucesso", "Etiqueta impressa com sucesso.")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro na Impressão",
                f"Ocorreu um erro ao tentar imprimir a etiqueta:\n\n{str(e)}",
            )
