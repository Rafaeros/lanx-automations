import asyncio
import os
import sys
from qasync import asyncSlot
from PySide6 import QtCore
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QDialog

from core.configs import Configs
from core.frontend.tabs.configs_tab import ConfigsTab
from core.orders import OrderManager
from core.session_manager import AuthOnCM
from core.utils.path_utils import resource_path
from core.frontend.tabs.add_operator_tab import AddOperatorTab
from core.frontend.tabs.main_tab import MainTab
from core.frontend.widgets.credentials_dialog_widget import CredentialsDialog
from core.utils.printer import PrinterManager

TMP_PATH = "tmp/reports"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.auth = AuthOnCM()
        self.configs = Configs()
        self.printer = PrinterManager()
        self.order_manager = OrderManager()
        self.setContentsMargins(0, 0, 0, 0)
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("Gerador de Etiqueta Teste Elétrico V1.0")
        self.setWindowIcon(QIcon(resource_path("core/assets/icon.png")))
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
        self.tabs.currentChanged.connect(self.tab_changed)

        if not self.configs.get("username") or not self.configs.get("password"):
            dlg = CredentialsDialog(self.configs, self)
            result = dlg.exec()

            if result != QDialog.Accepted:
                QMessageBox.critical(self, "Erro", "Credenciais não fornecidas.")
                return
        
        if self.order_manager.file_path is None:
            await self.auth.login()
            await self.auth.get_orders()

            QMessageBox.information(
                self, "Sucesso", "Ordens de produção carregadas com sucesso!"
            )

        self.tabs.addTab(MainTab(self.configs, self.printer), "Principal")
        self.tabs.addTab(AddOperatorTab(self.configs), "Adicionar Operador")
        self.tabs.addTab(ConfigsTab(self.configs, self.printer), "Configurações")
        self.tabs.setCurrentIndex(0)

        self.show()

    def tab_changed(self, index):
        print("tab changed to ", index)
