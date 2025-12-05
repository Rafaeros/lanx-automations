from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
)
from PySide6.QtGui import QIcon

from core.configs import Configs
from core.utils.path_utils import resource_path


class OperatorListWidget(QWidget):
    def __init__(self, configs: Configs, parent=None):
        super().__init__(parent)
        self.configs = configs
        self.v_layout = QVBoxLayout()
        self.h_layout = QHBoxLayout()

        self.remove_operator_btn = QPushButton("Remover Operador")
        self.remove_operator_btn.setIcon(QIcon(resource_path("core/assets/bin.png")))
        self.remove_operator_btn.setStyleSheet("background-color: red")
        self.operators_list = QListWidget()

        self.populate_list()

        self.remove_operator_btn.clicked.connect(self.remove_operator)
        self.h_layout.addWidget(self.remove_operator_btn)
        self.v_layout.addLayout(self.h_layout)
        self.v_layout.addWidget(self.operators_list)
        self.setLayout(self.v_layout)

    def populate_list(self):
        self.operators_list.clear()
        for operator in self.configs.operators:
            self.operators_list.addItem(operator["name"])

    def remove_operator(self):
        selected_item = self.operators_list.currentItem()
        if selected_item:
            self.configs.remove_operator(selected_item.text())
            self.populate_list()
