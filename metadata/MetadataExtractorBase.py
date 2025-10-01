from abc import ABC, abstractmethod

class MetadataExtractorBase(ABC):
    @abstractmethod
    def extract_metadata(self, file_path):
        """
        Extrae los metadatos de un archivo de audio.
        :param file_path: Ruta del archivo de audio.
        :return: Diccionario con los metadatos.
        """
        pass

    @abstractmethod
    def write_metadata(self, file_path, metadataLyrics):
        """
        Escribe los metadatos en un archivo de audio.
        :param file_path: Ruta del archivo de audio.
        :param metadataLyrics: Diccionario con los metadatos a escribir.
        """
        pass
    