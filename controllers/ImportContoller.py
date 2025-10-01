from PyQt6 import QtWidgets, uic
from pathlib import Path

class ImportContoller:
	"""
	Se encarga de gestionar la letra importada de Importar.py mediante el btn pushButtonImportar.
	Al pulsar el botón abre la ventana definida en gui/Importar.py (Ui_Importar) o, en su defecto,
	carga gui/Importar.ui con uic.loadUi.
	"""
	def __init__(self, ui, parent=None, verbose: bool = True):
		self.ui = ui
		self.parent = parent or ui
		self.verbose = verbose
		self.ui.pushButtonImportar.clicked.connect(self.on_import_clicked)

	def _populate_table_from_text(self, text: str) -> int:
		"""
		Convierte texto en líneas y lo coloca en tableWidgetLyrics.
		- Normaliza saltos de línea y elimina BOM/CR.
		- Inserta saltos de línea entre CJK (japonés) y texto latino (romaji) cuando faltan.
		- Elimina timestamps al inicio de línea (por ejemplo [00:09.60]) y deja la columna de marcadores vacía.
		Devuelve el número de líneas cargadas.
		"""
		try:
			import re
			table = self.ui.tableWidgetLyrics
			table.clearContents()
			table.setRowCount(0)

			ts_leading = re.compile(r'^\s*\[?\s*\d{1,2}:\d{2}(?:\.\d{1,3})?\s*\]?\s*')

			if not isinstance(text, str):
				return 0
			text_norm = text.replace('\r', '')
			if text_norm.startswith('\ufeff'):
				text_norm = text_norm.lstrip('\ufeff')

			text_norm = re.sub(r'[ \t]+', ' ', text_norm)

			cjk = r'\u4E00-\u9FFF\u3040-\u309F\u30A0-\u30FF'
			latin = r'A-Za-z\u00C0-\u024F0-9'
			pat_cjk_lat = re.compile(r'([{cjk}]+)\s*([{latin}][^{cjk}\n\r]+)'.format(cjk=cjk, latin=latin))
			pat_lat_cjk = re.compile(r'([{latin}][^{cjk}\n\r]+)\s*([{cjk}]+)'.format(cjk=cjk, latin=latin))

			prev = None
			iter_text = text_norm
			for _ in range(5):
				new = pat_cjk_lat.sub(r'\1\n\2', iter_text)
				new = pat_lat_cjk.sub(r'\1\n\2', new)
				if new == iter_text:
					break
				iter_text = new
			text_norm = iter_text

			lines_raw = text_norm.split('\n')
			lines = []
			for ln in lines_raw:
				s = ln.strip()
				if not s:
					continue
				s = ts_leading.sub('', s)
				s = re.sub(r'\s+', ' ', s).strip()
				if s:
					lines.append(s)

			for i, ln in enumerate(lines):
				table.insertRow(i)
				item_ts = QtWidgets.QTableWidgetItem("")
				item_lyrc = QtWidgets.QTableWidgetItem(ln)
				table.setItem(i, 0, item_ts)
				table.setItem(i, 1, item_lyrc)
			return len(lines)
		except Exception as e:
			if self.verbose:
				print(f"Error al poblar la tabla desde texto: {e}")
			return 0

	def on_import_clicked(self):
		"""Abrir la ventana de importación usando Ui_Importar o Importar.ui."""
		try:
			try:
				sel = self.ui.listViewBiblioteca.selectedIndexes()
				if not sel:
					QtWidgets.QMessageBox.warning(
						self.parent,
						"Importar",
						"Seleccione una canción en la biblioteca antes de usar Importar."
					)
					return
			except Exception:
				QtWidgets.QMessageBox.warning(
					self.parent,
					"Importar",
					"No se puede importar: listViewBiblioteca no disponible."
				)
				return

			module = None
			try:
				from gui import Importar as module
			except Exception:
				module = None

			if module and hasattr(module, "Ui_Importar"):
				try:
					ui_cls = getattr(module, "Ui_Importar")
					dlg = QtWidgets.QDialog(self.parent)
					ui = ui_cls()
					ui.setupUi(dlg)

					try:
						def _on_load_and_close():
							text = ui.textEditLyricsSet.toPlainText()
							count = self._populate_table_from_text(text)
							QtWidgets.QMessageBox.information(self.parent, "Importar", f"{count} líneas cargadas en la tabla.")
							dlg.accept()
						ui.pushButtonCargarLyrics.clicked.connect(_on_load_and_close)
					except Exception:
						if self.verbose:
							print("No se pudo conectar pushButtonCargarLyrics en Ui_Importar")

					dlg.exec()
					return
				except Exception as e:
					if self.verbose:
						print(f"Error usando Ui_Importar: {e}")

			ui_path = Path(__file__).resolve().parent.parent / "gui" / "Importar.ui"
			if ui_path.exists():
				try:
					dlg = QtWidgets.QDialog(self.parent)
					uic.loadUi(str(ui_path), dlg) # type: ignore
					try:
						def _on_load_and_close_uic():
							textedit = dlg.findChild(QtWidgets.QTextEdit, "textEditLyricsSet")
							if textedit:
								text = textedit.toPlainText()
								count = self._populate_table_from_text(text)
								QtWidgets.QMessageBox.information(self.parent, "Importar", f"{count} líneas cargadas en la tabla.")
							else:
								QtWidgets.QMessageBox.warning(self.parent, "Importar", "No se encontró textEditLyricsSet en el diálogo.")
							dlg.accept()
						btn = dlg.findChild(QtWidgets.QPushButton, "pushButtonCargarLyrics")
						if btn:
							btn.clicked.connect(_on_load_and_close_uic)
					except Exception as e:
						if self.verbose:
							print(f"No se pudo conectar pushButtonCargarLyrics en Importar.ui: {e}")

					dlg.exec()
					return
				except Exception as e:
					if self.verbose:
						print(f"Error cargando Importar.ui: {e}")

			QtWidgets.QMessageBox.warning(self.parent, "Importar", "No se encontró Importar (ni Importar.py ni Importar.ui).")
		except Exception as e:
			QtWidgets.QMessageBox.critical(self.parent, "Error", f"Ocurrió un error al abrir Importar: {e}")
			if self.verbose:
				print(f"Error en on_import_clicked: {e}")

