from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QDateEdit,
)
from PySide6.QtCore import QDate
from qasync import asyncSlot


class DateSelectWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        date_layout = QHBoxLayout(self)
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.setSpacing(20)

        # InitDate
        init_container = QHBoxLayout()
        init_container.setSpacing(15)
        self.init_date_label = QLabel("Data inicial:")
        self.init_date = QDateEdit()
        self.init_date.setStyleSheet("font-size: 14px;")
        self.init_date.setDisplayFormat("dd/MM/yyyy")
        self.init_date.setCalendarPopup(True)
        self.init_date.setDate(QDate.currentDate())
        init_container.addWidget(self.init_date_label)
        init_container.addWidget(self.init_date)

        # EndDate
        end_container = QHBoxLayout()
        end_container.setSpacing(15)
        self.end_date_label = QLabel("Data final:  ")
        self.end_date = QDateEdit()
        self.end_date.setStyleSheet("font-size: 14px;")
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addMonths(3))
        end_container.addWidget(self.end_date_label)
        end_container.addWidget(self.end_date)

        # Layout
        date_layout.addLayout(init_container)
        date_layout.addLayout(end_container)
        date_layout.addStretch(1)


    @asyncSlot()
    async def get_dates(self):
        """Retorna datas no formato padrão dd/MM/yyyy."""
        return (
            self.init_date.date().toString("dd/MM/yyyy"),
            self.end_date.date().toString("dd/MM/yyyy"),
        )
