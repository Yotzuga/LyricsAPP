from .MetadataExtractorBase import MetadataExtractorBase
from mutagen.flac import FLAC
from typing import Any, Dict, List, Optional

class FLACMetadataExtractor(MetadataExtractorBase):
    def _find_lyric_key(self, tags) -> Optional[str]:
        """Devuelve la primera clave en tags que parezca contener letras."""
        if not tags:
            return None
        for k in list(tags.keys()):
            lk = k.lower()
            if "lyric" in lk or "unsync" in lk or "comment" in lk:
                return k
        return None

    def extract_metadata(self, file_path) -> Dict[str, Any]:
        """
        Extrae metadatos de un archivo FLAC.
        :param file_path: Ruta del archivo FLAC.
        :return: Diccionario con los metadatos extraídos.
        """
        try:
            audio = FLAC(file_path)
            tags = audio.tags or {}

            duration = audio.info.total_samples / audio.info.sample_rate if audio.info else 0.0
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            milliseconds = int((duration % 1) * 1000)
            formatted_duration = f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"

            metadata: Dict[str, Any] = {
                "title": tags.get("TITLE", ["Desconocido"])[0] if tags and "TITLE" in tags and tags["TITLE"] else "Desconocido", # type: ignore
                "artist": tags.get("ARTIST", ["Desconocido"])[0] if tags and "ARTIST" in tags else "Desconocido", # type: ignore
                "album": tags.get("ALBUM", ["Desconocido"])[0] if tags and "ALBUM" in tags else "Desconocido", # type: ignore
                "duration": formatted_duration,
                "lyrics": []
            }

            if tags and tags.get("LYRICS") is not None: # type: ignore
                key = "LYRICS"
            else:
                key = self._find_lyric_key(tags)

            if key:
                val = tags.get(key) # type: ignore
                if isinstance(val, (list, tuple)):
                    lyrics_crudo = "\n".join(val)
                else:
                    lyrics_crudo = str(val)
                metadata["lyrics"] = self.formatear_Lyrics(lyrics_crudo)

            return metadata
        except Exception as e:
            print(f"Error al extraer metadatos del archivo FLAC {file_path}: {e}")
            return {
                "title": "Desconocido",
                "artist": "Desconocido",
                "album": "Desconocido",
                "duration": "00:00:000",
                "lyrics": []
            }

    def formatear_Lyrics(self, lyrics_crudo) -> List[Dict[str, str]]:
        """
        Procesa las letras crudas provenientes de los metadatos y las formatea en una estructura limpia.
        :param lyrics_crudo: Texto crudo de las letras con marcas de tiempo.
        :return: Lista de diccionarios con las letras formateadas.
        """
        lyrics_limpio: List[Dict[str, str]] = []
        try:
            lineas = lyrics_crudo.splitlines()
            for linea in lineas:
                if "[" in linea and "]" in linea:
                    ts_inicio = linea.find("[") + 1
                    ts_fin = linea.find("]")
                    timestamp = linea[ts_inicio:ts_fin].strip()
                    letra = linea[ts_fin + 1:].strip()

                    if timestamp and letra and not letra.isspace():
                        letra = letra.replace("\r", "").replace("\n", "")
                        lyrics_limpio.append({"ts": timestamp, "lyrc": letra})
        except Exception as e:
            print(f"Error al formatear las letras: {e}")
        return lyrics_limpio

    def write_metadata(self, file_path, metadataLyrics) -> bool:
        """
        Escribe los metadatos en un archivo FLAC.
        """
        try:
            audio = FLAC(file_path)

            if audio.tags is None:
                audio.add_tags()

            keys_to_delete = [k for k in list(audio.tags.keys()) if ("lyric" in k.lower() or "unsync" in k.lower() or "comment" in k.lower())] # type: ignore
            for k in keys_to_delete:
                try:
                    del audio.tags[k] # type: ignore
                except Exception:
                    pass

            if "lyrics" in metadataLyrics:
                lyrics = metadataLyrics["lyrics"]
                if isinstance(lyrics, list):
                    groups = []
                    current_ts = None
                    current_group = []
                    for entry in lyrics:
                        if "ts" not in entry or "lyrc" not in entry:
                            continue
                        ts = entry["ts"]
                        line = f"[{ts}] {entry['lyrc']}"
                        if ts != current_ts:
                            if current_group:
                                groups.append(current_group)
                            current_group = [line]
                            current_ts = ts
                        else:
                            current_group.append(line)
                    if current_group:
                        groups.append(current_group)
                    lyrics_text = "\n\n".join("\n".join(g) for g in groups)
                    audio.tags["LYRICS"] = [lyrics_text] # type: ignore
                else:
                    print("Error: El campo 'lyrics' debe ser una lista de diccionarios.")
                    return False

            audio.save()
            print(f"Letras sincronizadas guardadas correctamente en el archivo FLAC: {file_path}")
            return True
        except Exception as e:
            print(f"Error al guardar las letras sincronizadas en el archivo FLAC: {e}")
            return False


