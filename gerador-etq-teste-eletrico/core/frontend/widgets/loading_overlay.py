from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QProgressBar
from PySide6.QtCore import Qt


class LoadingOverlay(QWidget):
    def __init__(self, parent=None, message="Carregando OPs da Carga Máquina..."):
        super().__init__(parent)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            """
                    LoadingOverlay {
                        background-color: rgba(249, 243, 255, 230); 
                    }
                """
        )

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel(message)
        label.setObjectName("loadingLabel")
        label.setStyleSheet(
            """
            color: #7609e8;
            font-size: 16px;
            font-weight: 600;
        """
        )

        progress = QProgressBar()
        progress.setRange(0, 0)
        progress.setFixedWidth(250)
        progress.setStyleSheet(
            """
            QProgressBar {
                background-color: #e2e8f0;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                text-align: center;
                color: transparent;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7609e8, stop:1 #316ef3);
                border-radius: 6px;
            }
        """
        )

        layout.addWidget(label)
        layout.addSpacing(12)
        layout.addWidget(progress)

        self.hide()
