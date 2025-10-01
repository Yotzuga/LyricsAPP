from PyQt6 import QtCore, QtGui
from typing import Optional


class TimesController:
    """Maneja doble-clicks sobre `tableWidgetLyrics` para posicionar el player.

    - Lee el timestamp (columna 0) de la fila doble clickeada.
    - Convierte a milisegundos y llama a player.set_position(ms) sin detener la reproducción.
    - Actualiza la barra vertical delegando en `player_controller.slider_controller.update_from_time(ms)`
      si está disponible; si no, actualiza directamente `verticalSliderPlayerBar`.
    """

    def __init__(self, ui, player_controller: Optional[object] = None, verbose: bool = False):
        self.ui = ui
        self.player_controller = player_controller
        self.verbose = verbose
        self._original_styles = {}

        try:
            if hasattr(self.ui, 'tableWidgetLyrics'):
                self.ui.tableWidgetLyrics.doubleClicked.connect(self.on_table_double_clicked)
        except Exception:
            pass

    def _parse_timestamp_to_ms(self, ts: str) -> Optional[int]:
        """Parsea strings como M:SS.mmm o MM:SS.mmm a milisegundos. Devuelve None si no es válido."""
        if not ts or not isinstance(ts, str):
            return None
        s = ts.strip()
        try:
            parts = s.split(':')
            if len(parts) != 2:
                return None
            mins = int(parts[0])
            secs_ms = parts[1]
            if '.' in secs_ms:
                secs_str, ms_str = secs_ms.split('.', 1)
                secs = int(secs_str)
                # normalizar ms a 3 dígitos
                if len(ms_str) < 3:
                    ms_str = ms_str.ljust(3, '0')
                else:
                    ms_str = ms_str[:3]
                ms = int(ms_str)
            else:
                secs = int(secs_ms)
                ms = 0
            total_ms = (mins * 60 + secs) * 1000 + ms
            return int(total_ms)
        except Exception:
            return None

    def on_table_double_clicked(self, index: QtCore.QModelIndex):
        """Handler: obtener timestamp de la fila y posicionar el player en ms sin detener.

        Se espera que la columna 0 contenga el timestamp en formato M:SS.mmm.
        """
        try:
            row = index.row()
            ts_text = None
            try:
                item = self.ui.tableWidgetLyrics.item(row, 0)
                if item is not None:
                    ts_text = item.text()
            except Exception:
                ts_text = None

            if not ts_text:
                if self.verbose:
                    print(f"Timestamp vacío en fila {row}")
                return
            ms = self._parse_timestamp_to_ms(str(ts_text))
            if ms is None:
                if self.verbose:
                    print(f"Timestamp inválido en fila {row}: {ts_text}")
                return

            player = getattr(self.player_controller, 'player', None)
            if player is not None:
                try:
                    player.set_position(int(ms))
                except Exception:
                    if self.verbose:
                        print(f"Error al set_position({ms})")
            else:
                if self.verbose:
                    print('No hay player_controller conectado para set_position.')

            try:
                slider_controller = getattr(self.player_controller, 'slider_controller', None)
                if slider_controller is not None:
                    try:
                        slider_controller.update_from_time(int(ms))
                        return
                    except Exception:
                        pass

                total = 0
                try:
                    if self.player_controller is not None and hasattr(self.player_controller, '_total_ms'):
                        total = int(getattr(self.player_controller, '_total_ms') or 0)
                    elif player is not None and hasattr(player, 'get_length'):
                        total = int(player.get_length() or 0)
                except Exception:
                    total = 0

                if hasattr(self.ui, 'verticalSliderPlayerBar'):
                    try:
                        slider = self.ui.verticalSliderPlayerBar
                        if total > 0:
                            sv = max(0, min(total, total - int(ms)))
                        else:
                            sv = int(ms)
                        slider.blockSignals(True)
                        slider.setValue(int(sv))
                        slider.blockSignals(False)
                    except Exception:
                        pass
            except Exception:
                pass

        except Exception as e:
            if self.verbose:
                print(f"Error en on_table_double_clicked: {e}")

    def update_highlight(self, ms: int):
        """Resalta en la tabla las filas cuyo intervalo contiene `ms`.

        Se espera que la columna 0 contenga el timestamp de inicio de cada línea.
        La fila i cubre desde start_i hasta start_{i+1} (o hasta el final para la última fila).
        """
        try:
            table = getattr(self.ui, 'tableWidgetLyrics', None)
            if table is None:
                return

            rows = table.rowCount()
            if rows <= 0:
                return
            
            starts = []
            for i in range(rows):
                try:
                    item = table.item(i, 0)
                    ts = item.text() if item is not None else ''
                    tms = self._parse_timestamp_to_ms(ts) or 0
                except Exception:
                    tms = 0
                starts.append(int(tms))

            active_index = None
            for i in range(rows):
                start_i = starts[i]
                end_i = starts[i+1] if i+1 < rows else None
                if end_i is None:
                    if ms >= start_i:
                        active_index = i
                        break
                else:
                    if start_i <= ms < end_i:
                        active_index = i
                        break

            red_brush = QtGui.QBrush(QtGui.QColor('red'))
            for i in range(rows):
                try:
                    item_ts = table.item(i, 0)
                    item_ly = table.item(i, 1)


                    if i not in self._original_styles:
                        try:
                            orig_ts_brush = QtGui.QBrush(item_ts.foreground()) if item_ts is not None else None
                        except Exception:
                            orig_ts_brush = None
                        try:
                            orig_ts_font = QtGui.QFont(item_ts.font()) if item_ts is not None else None
                        except Exception:
                            orig_ts_font = None
                        try:
                            orig_ly_brush = QtGui.QBrush(item_ly.foreground()) if item_ly is not None else None
                        except Exception:
                            orig_ly_brush = None
                        try:
                            orig_ly_font = QtGui.QFont(item_ly.font()) if item_ly is not None else None
                        except Exception:
                            orig_ly_font = None
                        self._original_styles[i] = (orig_ts_brush, orig_ts_font, orig_ly_brush, orig_ly_font)

                    if i == active_index:
                        if item_ts:
                            try:
                                item_ts.setForeground(red_brush)
                            except Exception:
                                pass
                            try:
                                f = item_ts.font()
                                f.setBold(True)
                                item_ts.setFont(f)
                            except Exception:
                                pass
                        if item_ly:
                            try:
                                item_ly.setForeground(red_brush)
                            except Exception:
                                pass
                            try:
                                f2 = item_ly.font()
                                f2.setBold(True)
                                item_ly.setFont(f2)
                            except Exception:
                                pass
                    else:
                        orig = self._original_styles.get(i)
                        if orig is not None:
                            orig_ts_brush, orig_ts_font, orig_ly_brush, orig_ly_font = orig
                            if item_ts and orig_ts_brush is not None:
                                try:
                                    item_ts.setForeground(orig_ts_brush)
                                except Exception:
                                    pass
                            if item_ts and orig_ts_font is not None:
                                try:
                                    item_ts.setFont(QtGui.QFont(orig_ts_font))
                                except Exception:
                                    pass
                            if item_ly and orig_ly_brush is not None:
                                try:
                                    item_ly.setForeground(orig_ly_brush)
                                except Exception:
                                    pass
                            if item_ly and orig_ly_font is not None:
                                try:
                                    item_ly.setFont(QtGui.QFont(orig_ly_font))
                                except Exception:
                                    pass
                except Exception:
                    pass
        except Exception:
            if self.verbose:
                print('Error en update_highlight')
                
