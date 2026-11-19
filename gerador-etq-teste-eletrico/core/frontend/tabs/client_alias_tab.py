from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
)
from PySide6.QtGui import QIcon

from core.configs import Configs
from core.utils.path_utils import resource_path


class ClientAliasTab(QWidget):
    """Registers short names (aliases) printed on the label instead of the full client name."""

    def __init__(self, configs: Configs, parent=None):
        super().__init__(parent)
        self.configs = configs

        self.name_input = QLineEdit(placeholderText="Nome exato do cliente (como vem do relatório)")
        self.alias_input = QLineEdit(placeholderText="Ex: TRUCKSCONTROL")
        self.add_btn = QPushButton("Salvar Cliente")
        self.add_btn.setObjectName("primary")
        self.remove_btn = QPushButton("Remover Cliente")
        self.remove_btn.setIcon(QIcon(resource_path("core/assets/bin.png")))
        self.remove_btn.setObjectName("danger")
        self.list_widget = QListWidget()

        form = QFormLayout()
        form.addRow(QLabel("Nome do Cliente"), self.name_input)
        form.addRow(QLabel("Nome na Etiqueta"), self.alias_input)

        buttons = QHBoxLayout()
        buttons.addWidget(self.add_btn)
        buttons.addWidget(self.remove_btn)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(buttons)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

        self.add_btn.clicked.connect(self.add_alias)
        self.alias_input.returnPressed.connect(self.add_alias)
        self.remove_btn.clicked.connect(self.remove_alias)
        self.list_widget.itemClicked.connect(self.load_selected)
        self.populate_list()

    def populate_list(self):
        self.list_widget.clear()
        for item in self.configs.client_aliases:
            self.list_widget.addItem(f"{item['name']}  →  {item['alias']}")

    def load_selected(self):
        row = self.list_widget.currentRow()
        if row < 0:
            return
        item = self.configs.client_aliases[row]
        self.name_input.setText(item["name"])
        self.alias_input.setText(item["alias"])

    def add_alias(self):
        name = self.name_input.text().strip()
        alias = self.alias_input.text().strip()
        if not name or not alias:
            return
        self.configs.set_client_alias(name, alias)
        self.name_input.clear()
        self.alias_input.clear()
        self.populate_list()

    def remove_alias(self):
        row = self.list_widget.currentRow()
        if row < 0:
            return
        self.configs.remove_client_alias(self.configs.client_aliases[row]["name"])
        self.populate_list()
