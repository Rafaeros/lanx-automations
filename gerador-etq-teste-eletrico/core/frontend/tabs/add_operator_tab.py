from PySide6.QtWidgets import QWidget, QVBoxLayout

from core.configs import Configs
from core.frontend.widgets.add_operator_widget import AddOperatorWidget
from core.frontend.widgets.operator_list_widget import OperatorListWidget


class AddOperatorTab(QWidget):
    def __init__(self, configs: Configs, parent=None):
        super().__init__(parent)
        self.configs = configs

        self.main_layout = QVBoxLayout()
        self.add_operator_widget = AddOperatorWidget(self.configs)
        self.operator_list_widget = OperatorListWidget(self.configs)
        self.main_layout.addWidget(self.add_operator_widget)
        self.main_layout.addWidget(self.operator_list_widget)
        self.main_layout.addStretch(1)
        self.setLayout(self.main_layout)

        self.add_operator_widget.operator_added.connect(
            self.operator_list_widget.populate_list
        )
