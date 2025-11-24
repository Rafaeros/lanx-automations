import asyncio
import os
import sys
from qasync import asyncSlot
from PySide6 import QtCore
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QTabWidget,
)

from core.config_manager import Configs
from core.frontend.widgets.tabs.configs_tab_widget import ConfigsTab
from core.frontend.widgets.tabs.main_tab_widget import MainTab
from core.session_manager import AuthOnCM

TMP_PATH = "tmp/reports"


def resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.auth = AuthOnCM()
        self.configs = Configs()
        self.setContentsMargins(0, 0, 0, 0)
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("Gerador de Carteira PCP V1.0")
        self.setWindowIcon(QIcon(resource_path("core/assets/images/icon.png")))
        QtCore.QTimer.singleShot(0, self.setup_ui)

    def closeEvent(self, event):
        loop = asyncio.get_event_loop()
        loop.create_task(self.auth.close())
        self.configs.save()
        event.accept()

    @asyncSlot()
    async def setup_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.main_tab = MainTab(self.auth)
        self.configs_tab = ConfigsTab(self.configs)

        self.tabs.addTab(self.main_tab, "Principal")
        self.tabs.addTab(self.configs_tab, "Configurações")

        self.tabs.currentChanged.connect(self.tab_changed)

        self.show()

    def tab_changed(self, index):
        print("tab changed to ", index)
