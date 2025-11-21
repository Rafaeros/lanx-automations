from io import BytesIO
import logging
import pandas as pd
from qasync import asyncSlot
from PySide6 import QtWidgets, QtGui, QtCore
from core.logger import logger
from core.frontend.widgets.date_widget import DateSelectWidget
from core.frontend.widgets.terminal_widget import TerminalWidget
from core.qt_logger_handler import QtLogHandler
from core.session_manager import AuthOnCM
from core.config import settings
from core.utils.format_excel import format_data_for_excel
from services.scrape_reports import get_combined_report_data


class MainWindow(QtWidgets.QWidget):
    def __init__(self, auth: AuthOnCM, settings=settings, parent: QtWidgets.QWidget | None = None):
        super().__init__()
        self.auth = auth
        self.settings = settings
        self.setContentsMargins(0, 0, 0, 0)
        self.setWindowTitle("Gerador de Carteira PCP V1.0")
        QtCore.QTimer.singleShot(0, self._init_login)

    
    @asyncSlot()
    async def _init_login(self):
        logged = await self.auth.login()
        if logged:
            self.setup_ui()
        else:
            QtWidgets.QMessageBox.critical(
                self, "Erro na autenticação", "Falha na autenticação do Carga Maquina"
            )
            self.close()

    def setup_ui(self):
        self.splash = QtWidgets.QSplashScreen(
            QtGui.QPixmap("./core/assets/images/splash.png")
        )
        self.splash.show()
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.date_widget = DateSelectWidget(self)
        self.main_layout.addWidget(self.date_widget)
        btn = QtWidgets.QPushButton("Gerar relatório")
        btn.clicked.connect(self.generate_report)
        self.main_layout.addWidget(btn)
        self.terminal = TerminalWidget(self)
        qt_handler = QtLogHandler()
        qt_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
        )
        qt_handler.emitter.log_signal.connect(self.terminal.write)

        logger.addHandler(qt_handler)
        self.main_layout.addWidget(self.terminal)
        self.splash.finish(self)

    @asyncSlot()
    async def generate_report(self):
        dates = await self.date_widget.get_dates()
        urls = {
            "sales": settings.SALES_PENDING_ORDER_URL,
            "prod": settings.PROD_PENDING_ORDER_URL,
            "materials": settings.PENDING_MATERIALS_URL,
        }
        client = await self.auth.get_client()
        items = await get_combined_report_data(client, urls, dates[0], dates[1], self.auth.csrf_token)
        items_bytes = format_data_for_excel(items)
        df = pd.read_excel(BytesIO(items_bytes))
        df.to_excel("report.xlsx", index=False)
        QtWidgets.QMessageBox.information(
            self, "Relatório gerado", "Relatório gerado com sucesso em report.xlsx"
        )
