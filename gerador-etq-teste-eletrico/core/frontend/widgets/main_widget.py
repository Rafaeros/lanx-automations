from PySide6.QtWidgets import QWidget, QVBoxLayout

from core.configs import Configs
from core.frontend.widgets.search_production_ordr_widget import SearchProductOrderWidget
from core.frontend.widgets.select_operator_widget import SelectOperatorWidget


class MainWidget(QWidget):
    def __init__(self, configs: Configs, parent=None):
        super().__init__(parent)
        self.configs = configs
        self.main_layout = QVBoxLayout()
        self.operator_list_widget = SelectOperatorWidget(self.configs)
        self.search_product_order_widget = SearchProductOrderWidget(self.configs)
        self.main_layout.addWidget(self.operator_list_widget)
        self.main_layout.addWidget(self.search_product_order_widget)
        self.main_layout.addStretch(1)
        self.setLayout(self.main_layout)
