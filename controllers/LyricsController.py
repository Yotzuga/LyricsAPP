from PyQt6 import QtCore, QtWidgets
from typing import Optional
import re
from controllers.LyricsTimingService import LyricsTimingService
from controllers.LyricsSyncService import LyricsSyncService

class LyricsController:
    """Controlador para gestionar tableWidgetLyrics.
    Al hacer doble clic en una canción de listViewBiblioteca carga sus letras en la tabla.
    """
    def __init__(self, ui, biblioteca_controller, player_controller: Optional[object] = None, verbose: bool = True):
        self.ui = ui
        self.biblioteca_controller = biblioteca_controller
        self.player_controller = player_controller
        self.verbose = verbose

        self.ui.listViewBiblioteca.doubleClicked.connect(self.on_list_double_clicked)

        try:
            self.ui.pushButtonGuardar.clicked.connect(self.on_save_clicked)
        except Exception:
            pass

        try:
            if hasattr(self.ui, 'pushButtonAsignarRowTime'):
                btn = getattr(self.ui, 'pushButtonAsignarRowTime')
                btn.clicked.connect(lambda _=None: getattr(self, 'assign_label_time_to_nearest_empty')())
        except Exception:
            pass

        try:
            if hasattr(self.ui, 'pushButtonBackSync'):
                btnb = getattr(self.ui, 'pushButtonBackSync')
                btnb.clicked.connect(lambda _=None: getattr(self, 'remove_last_filled_marker')())
        except Exception:
            pass

        self.timing_service = LyricsTimingService()
        self.sync_service = LyricsSyncService(self.timing_service)

    def on_list_double_clicked(self, index: QtCore.QModelIndex):
        try:
            song = None
            if hasattr(self.biblioteca_controller, "get_selected_song"):
                song = self.biblioteca_controller.get_selected_song()
            if song is None:
                keys = list(self.biblioteca_controller.biblioteca.songs.keys())
                row = index.row()
                if 0 <= row < len(keys):
                    song = self.biblioteca_controller.biblioteca.songs[keys[row]]
            if song is None:
                if self.verbose:
                    print("No se encontró la canción seleccionada.")
                return
            self.load_song_to_table(song)

            try:
                if self.player_controller and hasattr(self.player_controller, "play_file"):
                    file_path = getattr(song, 'file_path', None)
                    if file_path:
                        try:
                            self.player_controller.play_file(file_path)  # type: ignore
                        except Exception as e:
                            if self.verbose:
                                print(f"Error al iniciar reproducción automática: {e}")
                else:
                    try:
                        if self.player_controller and hasattr(self.player_controller, "on_play_clicked"):
                            self.player_controller.on_play_clicked()  # type: ignore
                    except Exception:
                        if self.verbose:
                            print("Error al iniciar reproducción automática (fallback).")
            except Exception as e:
                if self.verbose:
                    print(f"Error al iniciar reproducción automática: {e}")
        except Exception as e:
            if self.verbose:
                print(f"Error al cargar la canción desde la lista: {e}")

    def _normalize_timestamp(self, ts: str) -> str:
        """
        Normaliza timestamps con milisegundos incompletos:
        - 00:09.60  -> 00:09.600
        - 3:00.9    -> 3:00.900
        - 00:18.9234 -> 00:18.923 (trunca a 3 dígitos)
        Si no concuerda con el patrón, devuelve ts sin cambios.
        """
        import re
        m = re.match(r"^(\d{1,2}):(\d{2})\.(\d{1,})$", ts.strip())
        if not m:
            return ts
        mins, secs, ms = m.groups()
        if len(ms) < 3:
            ms = ms.ljust(3, "0")
        elif len(ms) > 3:
            ms = ms[:3]
        return f"{mins}:{secs}.{ms}"

    def load_song_to_table(self, song) -> None:
        """Puebla tableWidgetLyrics con las letras de la canción y actualiza labels."""
        try:
            try:
                self.ui.labelTituloSet.setText(getattr(song, "title", "--"))
                self.ui.labelArtistaSet.setText(getattr(song, "artist", "--"))
                self.ui.labelAlbumSet.setText(getattr(song, "album", "--"))
                self.ui.labelDuracionSet.setText(getattr(song, "duration", "--"))
            except Exception:
                pass

            table = self.ui.tableWidgetLyrics

            table.clearContents()
            lyrics = getattr(song, "lyrics", []) or []
            table.setRowCount(0)

            for i, entry in enumerate(lyrics):
                ts = entry.get("ts", "")
                lyrc = entry.get("lyrc", "")

                ts_norm = self._normalize_timestamp(ts)

                table.insertRow(i)

                item_ts = QtWidgets.QTableWidgetItem(ts_norm)
                item_lyrc = QtWidgets.QTableWidgetItem(lyrc)

                table.setItem(i, 0, item_ts)
                table.setItem(i, 1, item_lyrc)
        except Exception as e:
            if self.verbose:
                print(f"Error al poblar la tabla de letras: {e}")

    def on_save_clicked(self):
        try:
            song = None
            if hasattr(self.biblioteca_controller, "get_selected_song"):
                song = self.biblioteca_controller.get_selected_song()
            if song is None:
                sel = self.ui.listViewBiblioteca.selectedIndexes()
                if sel:
                    row = sel[0].row()
                    keys = list(self.biblioteca_controller.biblioteca.songs.keys())
                    if 0 <= row < len(keys):
                        song = self.biblioteca_controller.biblioteca.songs[keys[row]]

            if song is None:
                QtWidgets.QMessageBox.warning(self.ui, "Guardar letras", "No hay canción seleccionada para guardar.")
                return False

            table = self.ui.tableWidgetLyrics
            rows = table.rowCount()
            if rows == 0:
                QtWidgets.QMessageBox.information(self.ui, "Guardar letras", "La tabla de letras está vacía. Nada que guardar.")
                return False

            ts_re = re.compile(r"^\d{1,2}:\d{2}\.\d{3}$")

            new_lyrics = []
            for i in range(rows):
                item_ts = table.item(i, 0)
                item_lyrc = table.item(i, 1)
                ts = item_ts.text().strip() if item_ts is not None else ""
                lyrc = item_lyrc.text().strip() if item_lyrc is not None else ""
                if not ts or not lyrc:
                    QtWidgets.QMessageBox.warning(self.ui, "Fila inválida", f"La fila {i+1} tiene timestamp o letra vacío. Complete todos los campos para guardar.")
                    return False
                if not ts_re.match(ts):
                    QtWidgets.QMessageBox.warning(self.ui, "Formato inválido", f"Timestamp inválido en la fila {i+1}: '{ts}'. El formato debe ser M:SS.mmm o MM:SS.mmm (ej. 3:00.590).")
                    return False
                new_lyrics.append({"ts": ts, "lyrc": lyrc})

            song.lyrics = new_lyrics
            ok = song.save_metadata()
            if ok:
                QtWidgets.QMessageBox.information(self.ui, "Guardar letras", "Letras guardadas correctamente.")
                return True
            else:
                QtWidgets.QMessageBox.critical(self.ui, "Guardar letras", "Error al guardar las letras. Consulte la consola para más detalles.")
                return False
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.ui, "Error", f"Ocurrió un error al intentar guardar: {e}")
            if self.verbose:
                print(f"Error en on_save_clicked: {e}")
            return False

    def _label_text_to_ms(self, txt: str) -> Optional[int]:
        return self.timing_service.parse_label_to_ms(txt)

    def _format_ms_to_timestamp(self, ms: int) -> str:
        return self.timing_service.format_ms(ms)

    def assign_label_time_to_nearest_empty(self):
        """Asigna el tiempo mostrado en `labelTimeSongNow` al marcador vacío más cercano.

        Búsqueda: si hay una fila seleccionada, busca la fila vacía (col 0) con menor distancia
        en número de filas a la fila seleccionada; si no hay selección, toma la primera vacía.
        Si no hay marcadores vacíos muestra un diálogo informativo.
        """
        try:
            # intentar leer tiempo directamente del player para evitar retrasos de UI
            ms = None
            try:
                player = getattr(self.player_controller, 'player', None)
                if player is not None and hasattr(player, 'get_time'):
                    try:
                        cur = int(player.get_time() or 0)
                        if cur >= 0:
                            ms = cur
                    except Exception:
                        ms = None
            except Exception:
                ms = None

            if ms is None:
                if not hasattr(self.ui, 'labelTimeSongNow'):
                    QtWidgets.QMessageBox.warning(self.ui, "Asignar tiempo", "No se encontró el label de tiempo en la UI.")
                    return
                label_txt = str(self.ui.labelTimeSongNow.text()).strip()
                ms = self._label_text_to_ms(label_txt)
                if ms is None:
                    QtWidgets.QMessageBox.warning(self.ui, "Formato inválido", "El tiempo actual no tiene un formato válido (M:SS.mmm).")
                    return

            table = self.ui.tableWidgetLyrics
            rows = table.rowCount()
            if rows <= 0:
                QtWidgets.QMessageBox.information(self.ui, "Asignar tiempo", "La tabla de letras está vacía.")
                return

            timestamps = []
            for i in range(rows):
                try:
                    item = table.item(i, 0)
                    txt = item.text() if item is not None else ''
                except Exception:
                    txt = ''
                timestamps.append(txt)

            sel = table.selectedIndexes()
            ref = sel[0].row() if sel else None

            res = self.sync_service.assign_time_to_nearest_empty(timestamps, ms, ref)
            if res is None:
                QtWidgets.QMessageBox.information(self.ui, "Asignar tiempo", "Todos los marcadores están llenos.")
                return

            best_row, ts_text = res
            try:
                item = table.item(best_row, 0)
                if item is None:
                    item = QtWidgets.QTableWidgetItem(ts_text)
                    table.setItem(best_row, 0, item)
                else:
                    item.setText(ts_text)
                table.scrollToItem(item)
                table.clearSelection()
                item.setSelected(True)
            except Exception:
                pass

        except Exception as e:
            if self.verbose:
                print(f"Error en assign_label_time_to_nearest_empty: {e}")

    def remove_last_filled_marker(self):
        """Busca desde el final la última fila cuyo marcador (col 0) está lleno y lo borra.

        Si todos los marcadores están vacíos muestra un diálogo informando.
        """
        try:
            table = self.ui.tableWidgetLyrics
            rows = table.rowCount()
            if rows <= 0:
                QtWidgets.QMessageBox.information(self.ui, "Back Sync", "La tabla de letras está vacía.")
                return

            timestamps = []
            for i in range(rows):
                try:
                    item = table.item(i, 0)
                    txt = item.text() if item is not None else ''
                except Exception:
                    txt = ''
                timestamps.append(txt)

            idx = self.sync_service.remove_last_filled(timestamps)
            if idx is None:
                QtWidgets.QMessageBox.information(self.ui, "Back Sync", "Todos los marcadores están vacíos.")
                return

            try:
                item = table.item(idx, 0)
                if item is None:
                    new_item = QtWidgets.QTableWidgetItem('')
                    table.setItem(idx, 0, new_item)
                    table.scrollToItem(new_item)
                    table.clearSelection()
                    new_item.setSelected(True)
                else:
                    item.setText('')
                    table.scrollToItem(item)
                    table.clearSelection()
                    item.setSelected(True)
            except Exception:
                pass

        except Exception as e:
            if self.verbose:
                print(f"Error en remove_last_filled_marker: {e}")

