from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
)

from core.configs import Configs


class CredentialFormsWidget(QWidget):
    def __init__(self, configs: Configs, parent=None):
        super().__init__(parent)
        self.configs = configs
        self.main_layout = QVBoxLayout()
        self.h_layout = QHBoxLayout()
        self.form_layout = QFormLayout()

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuário")
        self.user_input.setText(configs.get("username", ""))

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Senha")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setText(configs.get("password", ""))

        self.save_credentials_btn = QPushButton("Salvar")
        self.save_credentials_btn.clicked.connect(self.save_credentials)

        self.form_layout.addRow("Usuário:", self.user_input)
        self.form_layout.addRow("Senha:", self.pass_input)
        self.h_layout.addWidget(self.save_credentials_btn)
        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addLayout(self.h_layout)
        self.setLayout(self.main_layout)

    def save_credentials(self):
        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()

        if not username or not password:
            return

        self.configs.set("username", username)
        self.configs.set("password", password)
