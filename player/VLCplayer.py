import threading
import time

try:
    import vlc
except Exception:
    vlc = None


class VLCPlayer:
    """Pequeño wrapper alrededor de python-vlc para reproducir archivos.
    Métodos: play(file_path), stop(), set_volume(int), get_time(), get_length(), set_position(ms)
    """
    def __init__(self):
        self.instance = vlc.Instance() if vlc else None
        self.player = self.instance.media_player_new() if self.instance else None
        self._media = None
        self._lock = threading.RLock()

    def play(self, file_path: str) -> bool:
        if not vlc:
            raise RuntimeError("python-vlc no está disponible")
        with self._lock:
            try:
                self._media = self.instance.media_new(str(file_path)) # type: ignore
                self.player.set_media(self._media) # type: ignore
                self.player.play() # type: ignore
                time.sleep(0.05)
                return True
            except Exception as e:
                print(f"Error al reproducir {file_path}: {e}")
                return False

    def stop(self):
        if self.player:
            try:
                self.player.stop()
            except Exception:
                pass

    def pause(self):
        """Pausa la reproducción de forma explícita (no toggle).

        Usa `set_pause(True)` si está disponible en la API de python-vlc. Como
        fallback intenta consultar el estado y llamar a `pause()` sólo si
        parece que estaba reproduciendo.
        Devuelve True si el comando fue enviado, False en caso de error o si no hay player.
        """
        if not self.player:
            return False
        try:
            if hasattr(self.player, 'set_pause'):
                try:
                    self.player.set_pause(True)
                except Exception:
                    try:
                        self.player.pause()
                    except Exception:
                        return False
            else:
                try:
                    st = None
                    try:
                        st = self.player.get_state()
                    except Exception:
                        st = None
                    if st is None or str(st).lower().endswith('playing'):
                        self.player.pause()
                except Exception:
                    return False
            return True
        except Exception:
            return False



    def resume(self) -> bool:
        """Reanuda la reproducción del media actual si existe.
        Devuelve True si el comando fue enviado.
        """
        if not self.player:
            return False
        try:
            if hasattr(self.player, 'set_pause'):
                try:
                    self.player.set_pause(False)
                except Exception:
                    self.player.play()
            else:
                self.player.play()
            return True
        except Exception:
            return False

    def is_paused(self) -> bool:
        """Devuelve True si el estado es Paused (siempre que python-vlc esté disponible)."""
        if not self.player:
            return False
        try:
            state = None
            try:
                state = self.player.get_state()
            except Exception:
                state = None
            if state is not None:
                try:
                    return str(state).lower().endswith('paused')
                except Exception:
                    return False
            return False
        except Exception:
            return False

    def set_volume(self, vol: int):
        if self.player:
            try:
                self.player.audio_set_volume(max(0, min(100, int(vol))))
            except Exception:
                pass

    def get_time(self) -> int:
        """Devuelve el tiempo actual en milisegundos."""
        if self.player:
            try:
                return int(self.player.get_time() or 0)
            except Exception:
                return 0
        return 0

    def get_length(self) -> int:
        """Devuelve la duración total en milisegundos."""
        if self.player:
            try:
                return int(self.player.get_length() or 0)
            except Exception:
                return 0
        return 0

    def set_position(self, ms: int):
        """Posicionar en milisegundos."""
        if self.player:
            try:
                total = self.get_length()
                if total > 0:
                    pos = float(ms) / float(total)
                    self.player.set_position(max(0.0, min(1.0, pos)))
            except Exception:
                pass
