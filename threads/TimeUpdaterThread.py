from PyQt6 import QtCore
import time


class TimeUpdaterThread(QtCore.QThread):
    """Hilo que consulta periódicamente el tiempo de reproducción y emite señales.
    Señales: timeUpdated(ms:int), lengthUpdated(ms:int)
    """
    timeUpdated = QtCore.pyqtSignal(int)
    lengthUpdated = QtCore.pyqtSignal(int)

    def __init__(self, get_time_cb, get_length_cb, interval_ms: int = 20):
        super().__init__()
        self.get_time_cb = get_time_cb
        self.get_length_cb = get_length_cb
        self.interval = max(10, int(interval_ms)) / 1000.0
        self._running = False

    def run(self):
        self._running = True
        last_len = -1
        while self._running:
            try:
                ms = int(self.get_time_cb() or 0)
                total = int(self.get_length_cb() or 0)
                if total != last_len:
                    self.lengthUpdated.emit(total)
                    last_len = total
                self.timeUpdated.emit(ms)
            except Exception:
                pass
            time.sleep(self.interval)

    def stop(self):
        self._running = False
        try:
            self.quit()
            self.wait(500)
        except Exception:
            pass
