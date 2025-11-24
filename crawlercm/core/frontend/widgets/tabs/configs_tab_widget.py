from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
)
from core.config_manager import Configs


class ConfigsTab(QWidget):
    def __init__(self, configs: Configs, parent: QWidget | None = None):
        super().__init__(parent)
        self.configs = configs
        self.setContentsMargins(0, 0, 0, 0)
        self.main_layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()
        self.save_btn_layout = QHBoxLayout()
        self.footer_layout = QHBoxLayout()

        # Widgets
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

        dev = QLabel("Desenvolvido por: Rafael Costa")
        version = QLabel("Versão: 1.0.0")


        # Layouts
        self.save_btn_layout.addWidget(save_btn)
        self.footer_layout.addStretch()
        self.footer_layout.addWidget(dev)
        self.footer_layout.addWidget(version)
        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addLayout(self.save_btn_layout)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.footer_layout)

    def save_configs(self):
        try:
            for row in range(self.form_layout.rowCount()):
                label = self.form_layout.itemAt(row, QFormLayout.LabelRole)
                field = self.form_layout.itemAt(row, QFormLayout.FieldRole)
                if label is None or field is None:
                    continue
                key = label.widget().text().replace(":", "").lower()
                value = field.widget().text()
                self.configs.set(key, value)
            self.configs.load()
            QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar configurações: {e}")
