from pathlib import Path
from typing import Dict, List, Optional
from player.Song import Song  # Importación corregida

class Biblioteca:
    def __init__(self):
        self.songs: Dict[str, Song] = {}  # Diccionario para almacenar las canciones con file_path normalizada como clave

    def limpiar_biblioteca(self) -> None:
        """
        Limpia la biblioteca eliminando todas las canciones.
        """
        self.songs.clear()
        print("Biblioteca limpiada.")

    def cargar_desde_carpeta(self, folder_path: str, recursive: bool = True, verbose: bool = True) -> int:
        """
        Carga todas las canciones de una carpeta específica.
        :param folder_path: Ruta de la carpeta que contiene archivos de audio.
        :param recursive: Si True, busca en subcarpetas recursivamente.
        :param verbose: Si True, imprime progreso.
        :return: Número de canciones cargadas.
        """
        p = Path(folder_path)
        if not p.is_dir():
            print(f"Error: La carpeta '{folder_path}' no existe.")
            return 0

        self.limpiar_biblioteca()
        formatos_validos = {".mp3", ".flac", ".m4a"}
        canciones_cargadas = 0

        iterator = p.rglob("*") if recursive else p.iterdir()
        for f in iterator:
            if not f.is_file():
                continue
            if f.suffix.lower() not in formatos_validos:
                continue
            try:
                file_path = str(f.resolve())
            except Exception:
                file_path = str(f)

            # Evitar recargar duplicados
            if file_path in self.songs:
                if verbose:
                    print(f"Omitido (ya cargado): {file_path}")
                continue

            try:
                song = Song.from_file(file_path)
                self.songs[file_path] = song
                canciones_cargadas += 1
                if verbose:
                    print(f"Canción cargada: {song.title} - {song.artist}")
            except FileNotFoundError:
                if verbose:
                    print(f"Archivo no encontrado: {file_path}")
            except Exception as e:
                if verbose:
                    print(f"Error al cargar {file_path}: {e}")

        if verbose:
            print(f"Total de canciones cargadas: {canciones_cargadas}")
        return canciones_cargadas

    def listar_canciones(self) -> List[Song]:
        """
        Lista todas las canciones en la biblioteca.
        :return: Lista de canciones.
        """
        return list(self.songs.values())

    def get_song(self, file_path: str) -> Optional[Song]:
        """
        Recupera una canción por su ruta (acepta rutas no normalizadas).
        """
        try:
            key = str(Path(file_path).resolve())
        except Exception:
            key = file_path
        return self.songs.get(key)

