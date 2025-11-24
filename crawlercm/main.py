import sys
import asyncio
from pathlib import Path

from PySide6.QtWidgets import QApplication
from qasync import QEventLoop

from core.frontend.widgets.main_window import MainWindow
from core.logger import logger


def main():
    app = QApplication(sys.argv)
    theme_path = Path("./core/frontend/theme.qss")

    if theme_path.exists():
        qss = theme_path.read_text(encoding="utf-8")
        app.setStyleSheet(qss)
    else:
        logger.warning("⚠️ Arquivo theme.qss não encontrado — tema não aplicado.")

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    window = MainWindow()
    window.show()

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
