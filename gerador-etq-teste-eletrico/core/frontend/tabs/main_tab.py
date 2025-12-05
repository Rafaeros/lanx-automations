from PySide6.QtWidgets import QWidget, QVBoxLayout
from core.configs import Configs
from core.frontend.widgets.main_widget import MainWidget


class MainTab(QWidget):
    def __init__(self, configs: Configs,  parent=None):
        super().__init__(parent)
        self.configs = configs
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(MainWidget(self.configs))
        self.setLayout(self.main_layout)
