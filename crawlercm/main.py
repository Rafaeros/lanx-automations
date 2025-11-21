import sys
import asyncio
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop
from core.session_manager import AuthOnCM
from core.frontend.widgets.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    auth = AuthOnCM()
    window = MainWindow(auth)
    window.show()

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
