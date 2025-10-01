import mutagen.mp4
from .MetadataExtractorBase import MetadataExtractorBase  # Importación corregida
from typing import Any, Dict, List

class M4AMetadataExtractor(MetadataExtractorBase):
    def extract_metadata(self, file_path) -> Dict[str, Any]:
        """
        Extrae metadatos de un archivo M4A.
        :param file_path: Ruta del archivo M4A.
        :return: Diccionario con los metadatos extraídos.
        """
        try:
            audio = mutagen.mp4.MP4(file_path)
            tags = audio.tags
            
            duration = audio.info.length if audio.info else 0.0
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            milliseconds = int((duration % 1) * 1000)
            formatted_duration = f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"

            metadata: Dict[str, Any] = {
                "title": tags.get("\xa9nam", ["Desconocido"])[0] if tags and "\xa9nam" in tags else "Desconocido",  # type: ignore
                "artist": tags.get("\xa9ART", ["Desconocido"])[0] if tags and "\xa9ART" in tags else "Desconocido",  # type: ignore
                "album": tags.get("\xa9alb", ["Desconocido"])[0] if tags and "\xa9alb" in tags else "Desconocido",  # type: ignore
                "duration": formatted_duration,
                "lyrics": [] 
            }

            if tags and tags.get("©lyr") is not None:  # type: ignore[reportOperatorIssue]
                lyrics_crudo = "\n".join(tags["©lyr"])  # type: ignore[reportOperatorIssue]
                metadata["lyrics"] = self.formatear_Lyrics(lyrics_crudo)

            if tags and not metadata["lyrics"]:
                for key in list(tags.keys()):
                    lk = key.lower()
                    if "lyr" in lk or "lyric" in lk or "unsync" in lk or "cmt" in lk or "comment" in lk:
                        try:
                            lyrics_crudo = "\n".join(tags[key])  # type: ignore[reportOperatorIssue]
                        except Exception:
                            lyrics_crudo = str(tags[key])  # type: ignore[reportOperatorIssue]
                        metadata["lyrics"] = self.formatear_Lyrics(lyrics_crudo)
                        break

            return metadata
        except Exception as e:
            print(f"Error al extraer metadatos del archivo M4A {file_path}: {e}")
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
        Escribe los metadatos en un archivo M4A.
        """
        try:
            audio = mutagen.mp4.MP4(file_path)

            # Asegurar contenedor de tags
            if audio.tags is None:
                audio.add_tags()

            keys_to_delete = [k for k in list(audio.tags.keys()) if ("lyr" in k.lower() or "lyric" in k.lower() or "unsync" in k.lower() or "cmt" in k.lower() or "comment" in k.lower() or k.lower().startswith("----:com.apple.itunes:"))]  # type: ignore[reportOperatorIssue]
            for k in keys_to_delete:
                try:
                    del audio.tags[k]  # type: ignore[reportOperatorIssue]
                except Exception:
                    # ignorar errores individuales y continuar
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
                    audio["©lyr"] = [lyrics_text]
                else:
                    print("Error: El campo 'lyrics' debe ser una lista de diccionarios.")
                    return False

            audio.save()
            print(f"Letras sincronizadas guardadas correctamente en el archivo M4A: {file_path}")
            return True
        except Exception as e:
            print(f"Error al guardar las letras sincronizadas en el archivo M4A: {e}")
            return False