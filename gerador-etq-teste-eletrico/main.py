import sys
import asyncio
from pathlib import Path

from PySide6.QtWidgets import QApplication
from qasync import QEventLoop

from core.logger import logger
from core.frontend.interface import MainWindow
from core.frontend.interface import resource_path

    
def main():
    app = QApplication(sys.argv)
    theme_path = Path(resource_path("core/frontend/theme.qss"))

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
