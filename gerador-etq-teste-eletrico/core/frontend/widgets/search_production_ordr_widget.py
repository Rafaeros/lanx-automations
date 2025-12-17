from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QLineEdit,
    QPushButton,
    QLabel,
)
from core.configs import Configs
from core.orders import Order, OrderManager
ORDER_PATH = "tmp/reports/"

class SearchProductOrderWidget(QWidget):
    def __init__(self, configs: Configs, parent=None):
        super().__init__(parent)
        self.configs = configs
        self.main_layout = QVBoxLayout()
        self.order_manager = OrderManager()
        search_layout = QHBoxLayout()
        product_layout = QHBoxLayout()

        self.search_label = QLabel("Ordem de Produção")
        self.search_input = QLineEdit(placeholderText="Número da Ordem Ex: 2580")
        self.search_btn = QPushButton("Buscar")
        self.search_btn.clicked.connect(self.search_order)
        self.product_input = QLineEdit(placeholderText="Codigo do Produto", readOnly=True)
        self.quantity_input = QLineEdit(placeholderText="Quantidade")
        self.description_input = QLineEdit(placeholderText="Descrição", readOnly=True)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)

        product_layout.addWidget(self.product_input)
        product_layout.addWidget(self.quantity_input)

        self.main_layout.addWidget(self.search_label)
        self.main_layout.addLayout(search_layout)
        self.main_layout.addLayout(product_layout)
        self.main_layout.addWidget(self.description_input)

        self.setLayout(self.main_layout)

    def search_order(self):
        code = self.search_input.text()
        order: Order = self.order_manager.get_order_by_code(code)

        if order is None:
            self.product_input.setText("")
            self.quantity_input.setText("")
            self.description_input.setText("")
            QMessageBox.warning(self, "Aviso", "Ordem de Produção não encontrada")
            return

        self.product_input.setText(order.product)
        self.quantity_input.setText(str(order.quantity))
        self.description_input.setText(order.description)