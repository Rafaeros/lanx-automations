from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QProgressBar
from PySide6.QtCore import Qt

class LoadingOverlay(QWidget):
    def __init__(self, parent=None, message="Carregando OPs da Carga Máquina..."):
        super().__init__(parent)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            LoadingOverlay {
                background-color: rgba(18, 18, 18, 220);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel(message)
        label.setObjectName("loadingLabel")
        label.setStyleSheet("""
            color: #9B5BFF;
            font-size: 16px;
            font-weight: 600;
        """)

        progress = QProgressBar()
        progress.setRange(0, 0)
        progress.setFixedWidth(250)
        progress.setStyleSheet("""
            QProgressBar {
                background-color: #2A2A2A;
                border: 1px solid #3A3A3A;
                border-radius: 6px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #9B5BFF;
                border-radius: 6px;
            }
        """)

        layout.addWidget(label)
        layout.addSpacing(12)
        layout.addWidget(progress)

        self.hide()