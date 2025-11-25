import logging
import os
import pathlib
import sys
from qasync import asyncSlot
from datetime import datetime as dt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
    QLabel,
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from core.logger import logger
from core.qt_logger_handler import QtLogHandler
from core.frontend.widgets.date_widget import DateSelectWidget
from core.frontend.widgets.terminal_widget import TerminalWidget
from core.session_manager import AuthOnCM
from services.scrape_reports import get_combined_report_data
from core.utils.format_excel import format_data_for_excel


def resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class MainTab(QWidget):
    def __init__(self, auth: AuthOnCM, parent: QWidget | None = None):
        super().__init__(parent)
        self.auth = auth
        self.main_layout = QVBoxLayout(self)

        # Widget
        self.date_widget = DateSelectWidget(self)
        self.terminal = TerminalWidget(self)

        self.logo = QLabel()
        pixmap = QPixmap(resource_path("core/assets/images/splash-wbg.png"))
        self.logo.setPixmap(pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        btn = QPushButton("Gerar relatório")
        btn.clicked.connect(self.generate_report)

        # Logger
        qt_handler = QtLogHandler()
        qt_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
        )
        qt_handler.emitter.log_signal.connect(self.terminal.write)

        logger.addHandler(qt_handler)

        # Layout
        self.main_layout.addWidget(self.logo)
        self.main_layout.addSpacing(25)
        self.main_layout.addWidget(self.date_widget)
        self.main_layout.addWidget(btn)
        self.main_layout.addWidget(self.terminal)

    @asyncSlot()
    async def generate_report(self):
        try:
            client = await self.auth.get_client()
            today: dt = dt.now()
            output_path: str = (
                f"./tmp/reports/Relatório Carteira - {today.strftime('%d-%m-%Y')}.xlsx"
            )
            pathlib.Path(f"tmp/reports").mkdir(parents=True, exist_ok=True)

            dates = await self.date_widget.get_dates()
            urls = {
                "sales": f"{self.auth.base_url}/relatorio/venda/renderGridExportacaoPedidosPendentes",
                "prod": f"{self.auth.base_url}/relatorio/producao/exportarOrdensPendentesAnalitico",
                "materials": f"{self.auth.base_url}/pedido/exportarPedidoFaltaMP",
            }

            items = await get_combined_report_data(
                client, urls, dates[0], dates[1], self.auth.csrf_token
            )
            items_bytes = format_data_for_excel(items)
            with open(output_path, 'wb') as f:
                f.write(items_bytes)
            QMessageBox.information(
                self,
                "Relatório gerado",
                f"Relatório gerado com sucesso em {output_path}",
            )
        except BufferError as e:
            QMessageBox.critical(
                self,
                "Erro ao Salvar",
                f"Ocorreu um erro ao salvar o arquivo: {e}",
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro ao Salvar",
                f"Ocorreu um erro ao salvar o arquivo: {e}",
            )
