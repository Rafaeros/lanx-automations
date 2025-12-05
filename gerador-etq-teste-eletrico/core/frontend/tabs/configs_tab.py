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
        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(QLabel("Credencais CM"))
        self.main_layout.addWidget(CredentialFormsWidget(self.configs))
        self.main_layout.addWidget(QLabel("Impressora"))
        self.main_layout.addWidget(PrinterWidget(self.configs, self.printer))
        self.main_layout.addStretch()
        self.setLayout(self.main_layout)
