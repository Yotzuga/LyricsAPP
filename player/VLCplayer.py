import os
import threading
import time

# Intento robusto de cargar python-vlc en Windows añadiendo rutas de VLC
_vlc_import_error = None
_vlc_plugin_path = None
try:
    if os.name == "nt":
        # Permitir que el usuario fuerce la ruta con VLC_PATH
        candidate_paths = [
            os.environ.get("VLC_PATH"),
            r"C:\\Program Files\\VideoLAN\\VLC",
            r"C:\\Program Files (x86)\\VideoLAN\\VLC",
        ]
        for p in candidate_paths:
            if p and os.path.isdir(p):
                try:
                    # Python 3.8+ en Windows requiere registrar rutas de DLL
                    os.add_dll_directory(p)  # type: ignore[attr-defined]
                except Exception:
                    pass
                # Sugerir ruta de plugins a libvlc
                _vlc_plugin_path = os.path.join(p, "plugins")
                # Exportar para que libvlc la vea si hace falta
                if os.path.isdir(_vlc_plugin_path):
                    os.environ.setdefault("VLC_PLUGIN_PATH", _vlc_plugin_path)
                break
    import vlc  # type: ignore
except Exception as e:
    vlc = None  # type: ignore
    _vlc_import_error = str(e)


class VLCPlayer:
    """Pequeño wrapper alrededor de python-vlc para reproducir archivos.
    Métodos: play(file_path), stop(), set_volume(int), get_time(), get_length(), set_position(ms)
    """
    def __init__(self):
        # Construir la instancia con posibles flags útiles
        if vlc:
            args = ["--no-video", "--quiet"]
            try:
                self.instance = vlc.Instance(*args)  # type: ignore
            except Exception:
                # último intento sin argumentos
                try:
                    self.instance = vlc.Instance()  # type: ignore
                except Exception:
                    self.instance = None
        else:
            self.instance = None
        self.player = self.instance.media_player_new() if self.instance else None
        self._media = None
        self._lock = threading.RLock()

    def play(self, file_path: str) -> bool:
        if not vlc or not self.instance or not self.player:
            # Mensaje de diagnóstico útil
            msg = "python-vlc no está disponible"
            if _vlc_import_error:
                msg += f" ({_vlc_import_error})"
            raise RuntimeError(msg)
        with self._lock:
            try:
                # Asegura cadena de ruta simple (no URI) para Windows
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
