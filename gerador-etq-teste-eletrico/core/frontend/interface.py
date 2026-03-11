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
from core.frontend.widgets.loading_overlay import LoadingOverlay
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
        self.loading_overlay = LoadingOverlay(
            self, "Carregando OPs da Carga Máquina..."
        )
        # Initialize UI after the window is ready
        QtCore.QTimer.singleShot(0, self.setup_ui)

    def closeEvent(self, event):
        loop = asyncio.get_event_loop()
        loop.create_task(self.auth.close())
        self.configs.save()
        event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "loading_overlay") and self.loading_overlay is not None:
            self.loading_overlay.resize(self.size())

    @asyncSlot()
    async def setup_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.currentChanged.connect(self.tab_changed)
        self.show()

        if not self.configs.get("username") or not self.configs.get("password"):
            dlg = CredentialsDialog(self.configs, self)
            result = dlg.exec()

            if result != QDialog.Accepted:
                QMessageBox.critical(self, "Erro", "Credenciais não fornecidas.")
                return

        if self.order_manager.file_path is None:
            self.loading_overlay.resize(self.size())
            self.loading_overlay.raise_()
            self.loading_overlay.show()
            QtCore.QCoreApplication.processEvents()

            try:
                await self.auth.login()
                await self.auth.get_orders()

                QMessageBox.information(
                    self, "Sucesso", "Ordens de produção carregadas com sucesso!"
                )

            except Exception as e:
                QMessageBox.critical(
                    self, "Erro ao carregar OPs", f"Ocorreu um erro:\n{str(e)}"
                )

            finally:
                self.loading_overlay.hide()

        self.main_tab = MainTab(self.configs, self.printer)
        self.add_operator_tab = AddOperatorTab(self.configs)
        self.configs_tab = ConfigsTab(self.configs, self.printer)

        self.tabs.addTab(self.main_tab, "Principal")
        self.tabs.addTab(self.add_operator_tab, "Adicionar Operador")
        self.tabs.addTab(self.configs_tab, "Configurações")

        # Synchronize operator list when a new one is added
        self.add_operator_tab.add_operator_widget.operator_added.connect(
            self.main_tab.main_widget.operator_list_widget.populate
        )

        self.tabs.setCurrentIndex(0)

        self.show()

    def tab_changed(self, index):
        print("tab changed to ", index)
