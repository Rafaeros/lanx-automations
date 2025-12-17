from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QComboBox,
    QLabel
)

from core.configs import Configs

class SelectOperatorWidget(QWidget):
    def __init__(self, configs: Configs, parent=None):
        super().__init__(parent)
        self.configs = configs
        self.main_layout = QVBoxLayout()
        self.operator_label = QLabel("Operador")
        self.operator_combo_box = QComboBox()
        self.populate()
        self.main_layout.addWidget(self.operator_label)
        self.main_layout.addWidget(self.operator_combo_box)
        self.setLayout(self.main_layout)

    def populate(self):
        operators = self.configs.get("operators")
        if not operators:
            return

        for operator in operators:
            self.operator_combo_box.addItem(operator["name"])
