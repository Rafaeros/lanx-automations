# qt_log_handler.py
import logging
from PySide6.QtCore import QObject, Signal

class QtLogEmitter(QObject):
    log_signal = Signal(str)

class QtLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.emitter = QtLogEmitter()

    def emit(self, record):
        msg = self.format(record)
        self.emitter.log_signal.emit(msg)
