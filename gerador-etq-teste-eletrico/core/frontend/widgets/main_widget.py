from PySide6.QtWidgets import QWidget, QVBoxLayout

from core.configs import Configs
from core.frontend.widgets.select_operator_widget import SelectOperatorWidget


class MainWidget(QWidget):
    def __init__(self, configs: Configs, parent=None):
        super().__init__(parent)
        self.configs = configs
        self.main_layout = QVBoxLayout()
        self.operator_list_widget = SelectOperatorWidget(self.configs)
        self.main_layout.addWidget(self.operator_list_widget)
        self.setLayout(self.main_layout)
    