import asyncio
import logging
import pathlib
import pandas as pd
from io import BytesIO
from qasync import asyncSlot
from datetime import datetime as dt

from PySide6 import QtCore
from PySide6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QWidget,
)

from core.config_manager import Configs
from core.frontend.widgets.tabs.configs_tab_widget import ConfigsTab
from core.frontend.widgets.tabs.main_tab_widget import MainTab
from core.session_manager import AuthOnCM

TMP_PATH = "tmp/reports"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.auth = AuthOnCM()
        self.configs = Configs()
        self.setContentsMargins(0, 0, 0, 0)
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("Gerador de Carteira PCP V1.0")
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
