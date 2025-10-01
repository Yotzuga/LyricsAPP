from .MP3MetadataExtractor import MP3MetadataExtractor  
from .M4AMetadataExtractor import M4AMetadataExtractor  
from .FLACMetadataExtractor import FLACMetadataExtractor  


class MetadataExtractor:
    @staticmethod
    def get_extractor(file_path):
        try:
            if file_path.endswith(".mp3"):
                return MP3MetadataExtractor()
            elif file_path.endswith(".flac"):
                return FLACMetadataExtractor()
            elif file_path.endswith(".m4a"):
                return M4AMetadataExtractor()
            else:
                raise ValueError("Formato de archivo no soportado")
        except Exception as e:
            raise

    @staticmethod
    def extract_metadata(file_path):
        try:
            extractor = MetadataExtractor.get_extractor(file_path)
            return extractor.extract_metadata(file_path)
        except Exception as e:
            return {
                "title": "Desconocido",
                "artist": "Desconocido",
                "album_artist": "Desconocido",
                "album": "Desconocido",
                "duration": 0.0,
                "lyrics": "No se encontraron letras."
            }

    @staticmethod
    def write_metadata(file_path, metadata):
        """
        Escribe los metadatos en el archivo utilizando el extractor correspondiente.
        :param file_path: Ruta del archivo de audio.
        :param metadata: Diccionario con los metadatos a escribir.
        """
        try:
            extractor = MetadataExtractor.get_extractor(file_path)
            extractor.write_metadata(file_path, metadata)
        except Exception as e:
            print(f"Error al escribir los metadatos en el archivo {file_path}: {e}")
            raise
        
   