from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QLabel,
)


class CredentialsDialog(QDialog):
    def __init__(self, configs, parent=None):
        super().__init__(parent)
        self.configs = configs
        self.setWindowTitle("Configuração Inicial")
        self.setModal(True)
        self.setMinimumWidth(350)

        layout = QVBoxLayout()
        form = QFormLayout()
        layout.addWidget(QLabel("Credencais CM"))
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuário")
        self.user_input.setText(configs.get("username", ""))

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Senha")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setText(configs.get("password", ""))

        form.addRow("Usuário:", self.user_input)
        form.addRow("Senha:", self.pass_input)

        self.save_btn = QPushButton("Salvar")
        self.save_btn.clicked.connect(self.save_credentials)

        layout.addLayout(form)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def save_credentials(self):
        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()

        if not username or not password:
            return

        self.configs.set("username", username)
        self.configs.set("password", password)

        self.accept()
