from PyQt6 import QtCore
from player.VLCplayer import VLCPlayer
from threads.TimeUpdaterThread import TimeUpdaterThread
from controllers.VerticalSliderController import VerticalSliderController


class PlayerController:
	"""Controlador simple que conecta UI mínima con VLCPlayer.

	Mantiene el comportamiento esencial: Play/Pause toggle, Stop, volumen y seek.
	Si existe un `VerticalSliderController` lo usará para la barra de progreso.
	"""

	def __init__(self, ui, biblioteca_controller=None):
		self.ui = ui
		self.biblioteca_controller = biblioteca_controller
		self.times_controller = None

		self.player = VLCPlayer()
		self.time_thread = None
		self.slider_controller = None
		self._total_ms = 0

		if hasattr(self.ui, 'pushButtonPlay'):
			self.ui.pushButtonPlay.setCheckable(True)
			self.ui.pushButtonPlay.toggled.connect(self.on_play_toggled)
		if hasattr(self.ui, 'pushButtonStop'):
			self.ui.pushButtonStop.clicked.connect(self.on_stop_clicked)
		if hasattr(self.ui, 'verticalSliderVolumen'):
			self.ui.verticalSliderVolumen.valueChanged.connect(self.on_volume_changed)
		if hasattr(self.ui, 'verticalSliderPlayerBar'):
			try:
				self.slider_controller = VerticalSliderController(self.ui.verticalSliderPlayerBar, self.player)
			except Exception:
				self.slider_controller = None

	def _start_time_thread(self):
		if self.time_thread is not None:
			return
		self.time_thread = TimeUpdaterThread(self.player.get_time, self.player.get_length, interval_ms=100)
		self.time_thread.timeUpdated.connect(self._on_time_updated)
		self.time_thread.lengthUpdated.connect(self._on_length_updated)
		self.time_thread.start()

	def _stop_time_thread(self):
		if self.time_thread:
			self.time_thread.stop()
			self.time_thread = None

	def play_file(self, file_path: str) -> bool:
		"""Inicia reproducción y sincroniza estado del botón Play. Devuelve True si OK."""
		if not file_path:
			return False
		ok = self.player.play(file_path)
		if not ok:
			if hasattr(self.ui, 'pushButtonPlay'):
				btn = self.ui.pushButtonPlay
				btn.blockSignals(True)
				btn.setChecked(False)
				btn.setText('Play')
				btn.blockSignals(False)
			return False

		if hasattr(self.ui, 'pushButtonPlay'):
			btn = self.ui.pushButtonPlay
			btn.blockSignals(True)
			btn.setChecked(True)
			btn.setText('Pause')
			btn.blockSignals(False)

		total = int(self.player.get_length() or 0)
		if total > 0:
			self._total_ms = total
			if self.slider_controller:
				self.slider_controller.set_total_ms(total)

		self._start_time_thread()
		return True

	def on_play_toggled(self, checked: bool):
		"""Toggle Play/Pause: checked True -> play/resume, False -> pause."""
		if checked:
			if self.player.is_paused():
				self.player.resume()
				if hasattr(self.ui, 'pushButtonPlay'):
					self.ui.pushButtonPlay.setText('Pause')
				return

			song = None
			if self.biblioteca_controller and hasattr(self.biblioteca_controller, 'get_selected_song'):
				song = self.biblioteca_controller.get_selected_song()
			if song:
				file_path = getattr(song, 'file_path', None)
				if file_path:
					self.play_file(file_path)
				else:
					if hasattr(self.ui, 'pushButtonPlay'):
						btn = self.ui.pushButtonPlay
						btn.blockSignals(True)
						btn.setChecked(False)
						btn.setText('Play')
						btn.blockSignals(False)
			else:
				if hasattr(self.ui, 'pushButtonPlay'):
					btn = self.ui.pushButtonPlay
					btn.blockSignals(True)
					btn.setChecked(False)
					btn.setText('Play')
					btn.blockSignals(False)
		else:
			self.player.pause()
			if hasattr(self.ui, 'pushButtonPlay'):
				self.ui.pushButtonPlay.setText('Play')

	def on_stop_clicked(self):
		self.player.stop()
		self._stop_time_thread()
		if hasattr(self.ui, 'verticalSliderPlayerBar'):
			if self.slider_controller:
				self.slider_controller.reset_to_total()
			else:
				slider = self.ui.verticalSliderPlayerBar
				slider.blockSignals(True)
				slider.setValue(int(self._total_ms or 0))
				slider.blockSignals(False)
		if hasattr(self.ui, 'labelTimeSongNow'):
			self.ui.labelTimeSongNow.setText('00:00.000')
		if hasattr(self.ui, 'pushButtonPlay'):
			btn = self.ui.pushButtonPlay
			btn.blockSignals(True)
			btn.setChecked(False)
			btn.setText('Play')
			btn.blockSignals(False)

	def on_volume_changed(self, value: int):
		self.player.set_volume(int(value))

	def on_seek_released(self):
		if self.slider_controller:
			self.slider_controller.on_seek_released()
			return

		total = int(self.player.get_length() or 0)
		if total > 0:
			self._total_ms = total
			if hasattr(self.ui, 'verticalSliderPlayerBar'):
				val = int(self.ui.verticalSliderPlayerBar.value())
				ms = max(0, min(total, total - val))
				self.player.set_position(int(ms))

	def _on_time_updated(self, ms: int):
		if hasattr(self.ui, 'labelTimeSongNow'):
			s = int(ms // 1000)
			m = s // 60
			s = s % 60
			ms_part = ms % 1000
			txt = f"{m:02d}:{s:02d}.{ms_part:03d}"
			self.ui.labelTimeSongNow.setText(txt)
		if self.slider_controller:
			try:
				self.slider_controller.update_from_time(int(ms))
			except Exception:
				pass
		else:
			if hasattr(self.ui, 'verticalSliderPlayerBar'):
				total = int(self._total_ms or 0)
				if total > 0:
					sv = max(0, min(total, total - int(ms)))
				else:
					sv = int(ms)
				self.ui.verticalSliderPlayerBar.blockSignals(True)
				self.ui.verticalSliderPlayerBar.setValue(int(sv))
				self.ui.verticalSliderPlayerBar.blockSignals(False)

		try:
			tc = getattr(self, 'times_controller', None)
			if tc is not None:
				try:
					tc.update_highlight(int(ms))
				except Exception:
					pass
		except Exception:
			pass

	def _on_length_updated(self, total_ms: int):
		t = max(1, int(total_ms))
		self._total_ms = t
		if hasattr(self.ui, 'verticalSliderPlayerBar'):
			slider = self.ui.verticalSliderPlayerBar
			slider.blockSignals(True)
			slider.setRange(0, t)
			slider.setValue(t)
			slider.blockSignals(False)
		else:
			slider = self.ui.verticalSliderPlayerBar
