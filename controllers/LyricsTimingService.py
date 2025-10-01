from typing import Optional, List
import re


class LyricsTimingService:
    """Servicio pequeño para parsear/formatear timestamps y encontrar marcadores vacíos.

    No depende de widgets, opera con listas de strings (timestamps tal como están en la tabla).
    """

    def __init__(self, prefer_forward: bool = True):
        # prefer_forward en caso de empate podría usarse para desempatar hacia adelante
        self.prefer_forward = bool(prefer_forward)

    def parse_label_to_ms(self, txt: str) -> Optional[int]:
        """Parsea strings como M:SS.mmm o MM:SS.mmm a milisegundos. Devuelve None si inválido."""
        if not txt or not isinstance(txt, str):
            return None
        m = re.match(r"^\s*(\d{1,2}):(\d{2})\.(\d{1,3})\s*$", txt)
        if not m:
            return None
        try:
            mins = int(m.group(1))
            secs = int(m.group(2))
            ms_str = m.group(3)
            if len(ms_str) < 3:
                ms_str = ms_str.ljust(3, '0')
            else:
                ms_str = ms_str[:3]
            ms = int(ms_str)
            total = (mins * 60 + secs) * 1000 + ms
            return int(total)
        except Exception:
            return None

    def format_ms(self, ms: int) -> str:
        """Formatea ms a M:SS.mmm (mins no forzado a 2 dígitos)."""
        try:
            m = int(ms // 60000)
            s = int((ms % 60000) // 1000)
            ms_part = int(ms % 1000)
            return f"{m}:{s:02d}.{ms_part:03d}"
        except Exception:
            return "0:00.000"

    def find_nearest_empty_row(self, timestamps: List[str], ref_index: Optional[int] = None) -> Optional[int]:
        """Dada una lista de timestamps (strings), devuelve el índice de la fila vacía más cercana.

        - timestamps: lista de textos tal cual aparecen en la columna de timestamps ('' o None = vacío)
        - ref_index: índice de referencia (fila seleccionada). Si None usa 0.
        Retorna el índice o None si no hay vacíos.
        """
        if not isinstance(timestamps, list):
            return None
        rows = len(timestamps)
        if rows == 0:
            return None

        empty_rows = [i for i, t in enumerate(timestamps) if not (t and str(t).strip())]
        if not empty_rows:
            return None

        if ref_index is None or not (0 <= ref_index < rows):
            # fallback: primera vacía
            return empty_rows[0]

        # buscar distancia mínima
        best = None
        best_dist = None
        for r in empty_rows:
            dist = abs(r - ref_index)
            if best_dist is None or dist < best_dist:
                best_dist = dist
                best = r
            elif dist == best_dist:
                # desempate: prefer_forward si configurado
                if self.prefer_forward and best is not None:
                    if r > best:
                        best = r
        return best
