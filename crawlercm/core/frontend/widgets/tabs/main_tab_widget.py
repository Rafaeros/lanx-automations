import logging
import pathlib
import pandas as pd
from qasync import asyncSlot
from datetime import datetime as dt
from io import BytesIO
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
)
from core.logger import logger
from core.qt_logger_handler import QtLogHandler
from core.frontend.widgets.date_widget import DateSelectWidget
from core.frontend.widgets.terminal_widget import TerminalWidget
from core.session_manager import AuthOnCM
from services.scrape_reports import get_combined_report_data
from core.utils.format_excel import format_data_for_excel


class MainTab(QWidget):
    def __init__(self, auth: AuthOnCM, parent: QWidget | None = None):
        super().__init__(parent)
        self.auth = auth
        self.main_layout = QVBoxLayout(self)
        self.date_widget = DateSelectWidget(self)
        self.main_layout.addWidget(self.date_widget)
        btn = QPushButton("Gerar relatório")
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

    @asyncSlot()
    async def generate_report(self):
        today: dt = dt.now()
        output_path: str = (
            f"./tmp/reports/Relatório Carteira - {today.strftime('%d-%m-%Y')}.xlsx"
        )
        pathlib.Path(f"tmp/reports").mkdir(parents=True, exist_ok=True)

        dates = await self.date_widget.get_dates()
        urls = {
            "sales": "https://v2.cargamaquina.com.br/relatorio/venda/renderGridExportacaoPedidosPendentes",
            "prod": "https://v2.cargamaquina.com.br/relatorio/producao/exportarOrdensPendentesAnalitico",
            "materials": "https://v2.cargamaquina.com.br/pedido/exportarPedidoFaltaMP",
        }

        client = await self.auth.get_client()
        items = await get_combined_report_data(
            client, urls, dates[0], dates[1], self.auth.csrf_token
        )
        items_bytes = format_data_for_excel(items)
        df = pd.read_excel(BytesIO(items_bytes))
        df.to_excel(output_path, index=False, sheet_name="Relatório")
        QMessageBox.information(
            self,
            "Relatório gerado",
            f"Relatório gerado com sucesso em {output_path}.xlsx",
        )
