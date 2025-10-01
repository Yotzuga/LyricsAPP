from PyQt6 import QtCore
from typing import Optional


class VerticalSliderController:
    """Controlador dedicado para `verticalSliderPlayerBar`.
    Gestiona conexiones del slider, debounce de seeks y mapeo invertido
    (visual -> ms = total_ms - slider_value).
    """
    def __init__(self, slider_widget, player, seek_debounce_ms: int = 150, verbose: bool = False):
        self.slider = slider_widget
        self.player = player
        self.verbose = verbose

        self._total_ms = 0
        self._pending_seek_val: Optional[int] = None
        self._seek_debounce_ms = int(seek_debounce_ms)
        self._seek_immediate = False
        self._user_seeking = False

        self._seek_timer = QtCore.QTimer()
        self._seek_timer.setSingleShot(True)
        self._seek_timer.timeout.connect(self._perform_seek_from_pending)

        try:
            self.slider.sliderReleased.connect(self.on_seek_released)
            self.slider.valueChanged.connect(self.on_playerbar_value_changed)
        except Exception:
            pass
        try:
            self.slider.sliderPressed.connect(self._on_playerbar_pressed)
        except Exception:
            pass
        try:
            self.slider.sliderMoved.connect(self._on_playerbar_moved)
        except Exception:
            pass

    def set_total_ms(self, total: int):
        try:
            t = max(1, int(total))
            self._total_ms = t
            try:
                self._seek_timer.stop()
            except Exception:
                pass
            self._pending_seek_val = None

            try:
                self.slider.blockSignals(True)
            except Exception:
                pass
            try:
                self.slider.setRange(0, t)
                try:
                    self.slider.setSingleStep(1000)
                    self.slider.setPageStep(max(10000, t // 10))
                except Exception:
                    pass
                self.slider.setValue(t)
            except Exception:
                pass
            try:
                self.slider.blockSignals(False)
            except Exception:
                pass
        except Exception:
            if self.verbose:
                print('Error en set_total_ms')

    def reset_to_total(self):
        try:
            try:
                self._seek_timer.stop()
            except Exception:
                pass
            self._pending_seek_val = None
            try:
                self.slider.blockSignals(True)
                self.slider.setValue(int(self._total_ms or 0))
                self.slider.blockSignals(False)
            except Exception:
                pass
        except Exception:
            pass

    def on_seek_released(self):
        self._user_seeking = False
        try:
            total_now = int(self.player.get_length() or 0)
            if total_now > 0 and total_now != int(self._total_ms or 0):
                self.set_total_ms(total_now)
        except Exception:
            pass

        try:
            val = int(self.slider.value())
            total = int(self._total_ms or 0)
            ms = max(0, min(total, total - val))
            self.player.set_position(int(ms))
        except Exception:
            pass

    def on_playerbar_value_changed(self, val: int):
        if not getattr(self, '_user_seeking', False):
            return

        if getattr(self, '_seek_immediate', False):
            total = int(self._total_ms or 0)
            ms = max(0, min(total, total - int(val)))
            self.player.set_position(int(ms))
            return

        self._pending_seek_val = int(val)
        try:
            self._seek_timer.start(self._seek_debounce_ms)
        except Exception:
            pass

    def _perform_seek_from_pending(self):
        val = self._pending_seek_val
        if val is None:
            return
        total = int(self._total_ms or 0)
        ms = max(0, min(total, total - int(val)))
        try:
            self.player.set_position(int(ms))
        except Exception:
            pass
        self._pending_seek_val = None

    def _on_playerbar_pressed(self):
        self._user_seeking = True
        try:
            self._seek_timer.stop()
        except Exception:
            pass
        self._pending_seek_val = None

    def _on_playerbar_moved(self, val: int):
        self._user_seeking = True
        try:
            self._seek_timer.stop()
        except Exception:
            pass
        self._pending_seek_val = None
        try:
            total_now = int(self.player.get_length() or 0)
            if total_now > 0 and total_now != int(self._total_ms or 0):
                self.set_total_ms(total_now)
        except Exception:
            pass

        if getattr(self, '_seek_immediate', False):
            total = int(self._total_ms or 0)
            ms = max(0, min(total, total - int(val)))
            try:
                self.player.set_position(int(ms))
            except Exception:
                pass
            return

        self._pending_seek_val = int(val)
        try:
            self._seek_timer.start(self._seek_debounce_ms)
        except Exception:
            pass

    def update_from_time(self, ms: int):
        try:
            total = int(self._total_ms or 0)
            if total <= 0:
                try:
                    total_now = int(self.player.get_length() or 0)
                    if total_now > 0:
                        self.set_total_ms(total_now)
                        total = int(self._total_ms or 0)
                except Exception:
                    pass

            if total > 0:
                val = max(0, min(total, total - int(ms)))
            else:
                val = int(ms)

            try:
                self.slider.blockSignals(True)
            except Exception:
                pass
            try:
                self.slider.setValue(int(val))
            except Exception:
                pass
            try:
                self.slider.blockSignals(False)
            except Exception:
                pass
        except Exception:
            pass
