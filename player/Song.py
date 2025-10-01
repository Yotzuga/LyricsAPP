from metadata.MetadataExtractor import MetadataExtractor  
from typing import Any, Dict, List, Optional

class Song:
    def __init__(self, title: str, artist: str, album: str, duration: Any, lyrics: Optional[List[Dict[str, Any]]] = None, file_path: Optional[str] = None):
        """
        Inicializa una instancia de Song.
        - duration: puede ser cadena formateada ("MM:SS:MS") o float segundos según tu extractor.
        - lyrics: lista de diccionarios con {"ts": "...", "lyrc":"..."} o estructura equivalente.
        """
        self.title = title
        self.artist = artist
        self.album = album
        self.duration = duration
        self.lyrics = lyrics if isinstance(lyrics, list) else []  
        self.file_path = file_path

    @classmethod
    def from_file(cls, file_path: str):
        """
        Crea una instancia de Song a partir de un archivo de audio.
        """
        try:
            metadata = MetadataExtractor.extract_metadata(file_path)
            title = metadata.get("title", "Desconocido")
            artist = metadata.get("artist", "Desconocido")
            album = metadata.get("album", "Desconocido")
            duration = metadata.get("duration", "00:00:000") 
            lyrics = metadata.get("lyrics", []) or []
            return cls(title=title, artist=artist, album=album, duration=duration, lyrics=lyrics, file_path=file_path)
        except Exception as e:
            print(f"Error al procesar el archivo {file_path}: {e}")
            return cls(title="Desconocido", artist="Desconocido", album="Desconocido", duration="00:00:000", lyrics=[], file_path=file_path)

    def save_metadata(self) -> bool:
        """
        Guarda únicamente el metadato de las letras (lyrics) en el archivo de audio utilizando la factoría MetadataExtractor.
        """
        if not self.file_path:
            print("No se puede guardar los metadatos porque no se especificó la ruta del archivo.")
            return False

        if not isinstance(self.lyrics, list):
            print("Las letras deben ser una lista antes de guardar.")
            return False

        try:
            MetadataExtractor.write_metadata(self.file_path, {"lyrics": self.lyrics})
            print(f"Letras guardadas correctamente en el archivo: {self.file_path}")
            return True
        except Exception as e:
            print(f"Error al guardar las letras en el archivo {self.file_path}: {e}")
            return False