from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)
from core.configs import Configs


class AddOperatorWidget(QWidget):
    operator_added = Signal()

    def __init__(self, configs: Configs, parent=None):
        super().__init__(parent)
        self.configs = configs
        self.v_layout = QVBoxLayout()
        self.h_layout = QHBoxLayout()
        self.form_layout = QFormLayout()

        self.name = QLabel("Nome do Operador")
        self.name_input = QLineEdit()
        self.add_operator_btn = QPushButton("Adicionar Operador")

        self.form_layout.addRow(self.name, self.name_input)
        self.h_layout.addLayout(self.form_layout)
        self.h_layout.addWidget(self.add_operator_btn)
        self.v_layout.addLayout(self.h_layout)
        self.v_layout.addStretch()
        self.setLayout(self.v_layout)

        self.add_operator_btn.clicked.connect(self.add_operator)

    def add_operator(self):
        name = self.name_input.text().strip()
        if not name:
            return
        self.configs.operators.append({"name": name})
        self.configs.save()
        self.name_input.clear()
        self.operator_added.emit()
