from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from core.configs import Configs
from core.frontend.widgets.credentials_form_widget import CredentialFormsWidget
from core.frontend.widgets.printer_widget import PrinterWidget
from core.utils.printer import PrinterManager


class ConfigsTab(QWidget):
    def __init__(self, configs: Configs, printer: PrinterManager, parent=None):
        super().__init__(parent)
        self.configs = configs
        self.printer = printer
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(10)

        cred_label = QLabel("Credenciais Carga Máquina")
        cred_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #7c3aed;")

        printer_label = QLabel("Configuração de Impressora")
        printer_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #7c3aed; margin-top: 20px;"
        )

        self.main_layout.addWidget(cred_label)
        self.main_layout.addWidget(CredentialFormsWidget(self.configs))
        self.main_layout.addWidget(printer_label)
        self.main_layout.addWidget(PrinterWidget(self.configs, self.printer))

        self.main_layout.addStretch()
        self.setLayout(self.main_layout)
