from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
)
from core.config_manager import Configs


class ConfigsTab(QWidget):
    def __init__(self, configs: Configs, parent: QWidget | None = None):
        super().__init__(parent)
        self.configs = configs
        self.main_layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()
        self.h_layout = QHBoxLayout()

        for key, value in self.configs.data.items():
            label = QLabel(f"{key}:".title())
            if key == "password":
                line_edit = QLineEdit(value)
                line_edit.setEchoMode(QLineEdit.Password)
            else:
                line_edit = QLineEdit(value)

            self.form_layout.addRow(label, line_edit)

        save_btn = QPushButton("Salvar")
        save_btn.clicked.connect(self.save_configs)

        self.h_layout.addWidget(save_btn)
        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addLayout(self.h_layout)

    def save_configs(self):
        for row in range(self.form_layout.rowCount()):
            label = self.form_layout.itemAt(row, QFormLayout.LabelRole)
            field = self.form_layout.itemAt(row, QFormLayout.FieldRole)
            if label is None or field is None:
                continue
            key = label.widget().text().replace(":", "").lower()
            value = field.widget().text()
            self.configs.set(key, value)
        self.configs.load()
