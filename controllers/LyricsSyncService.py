from typing import Optional, List, Tuple
from controllers.LyricsTimingService import LyricsTimingService


class LyricsSyncService:
    """Servicio para operaciones de sincronización sobre listas de timestamps.

    Opera sobre datos (listas de strings) y no sobre widgets.
    """

    def __init__(self, timing_service: Optional[LyricsTimingService] = None, prefer_forward: bool = True):
        self.timing = timing_service or LyricsTimingService(prefer_forward=prefer_forward)

    def assign_time_to_nearest_empty(self, timestamps: List[str], ms: int, ref_index: Optional[int] = None) -> Optional[Tuple[int, str]]:
        """Devuelve (row_index, formatted_timestamp) o None si no hay vacíos.

        - timestamps: lista de strings tal cual aparecen en la columna ('' o None = vacío)
        - ms: tiempo en milisegundos a asignar
        - ref_index: fila de referencia (opcional)
        """
        if not isinstance(timestamps, list):
            return None
        row = self.timing.find_nearest_empty_row(timestamps, ref_index)
        if row is None:
            return None
        ts_text = self.timing.format_ms(ms)
        return (row, ts_text)

    def remove_last_filled(self, timestamps: List[str]) -> Optional[int]:
        """Busca desde el final y devuelve el índice de la última fila que tenía timestamp lleno.

        Retorna None si no encontró ninguno.
        """
        if not isinstance(timestamps, list):
            return None
        for i in range(len(timestamps) - 1, -1, -1):
            t = timestamps[i]
            if t and str(t).strip():
                return i
        return None
