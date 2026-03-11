from PySide6.QtWidgets import QWidget, QVBoxLayout
from core.configs import Configs
from core.frontend.widgets.main_widget import MainWidget
from core.utils.printer import PrinterManager


class MainTab(QWidget):
    def __init__(self, configs: Configs, printer: PrinterManager, parent=None):
        super().__init__(parent)
        self.configs = configs
        self.printer = printer
        self.main_layout = QVBoxLayout()
        self.main_widget = MainWidget(self.configs, self.printer)
        self.main_layout.addWidget(self.main_widget)
        self.setLayout(self.main_layout)
