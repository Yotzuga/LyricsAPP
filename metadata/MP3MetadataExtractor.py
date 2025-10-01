from .MetadataExtractorBase import MetadataExtractorBase
from mutagen import File # type: ignore
from mutagen.id3 import ID3, USLT, ID3NoHeaderError # type: ignore
from typing import Any, Dict

class MP3MetadataExtractor(MetadataExtractorBase):
    def extract_metadata(self, file_path) -> Dict[str, Any]:
        try:
            audio = File(file_path)
            duration = audio.info.length if audio and getattr(audio, "info", None) else 0.0

            minutes = int(duration // 60)
            seconds = int(duration % 60)
            milliseconds = int((duration % 1) * 1000)
            formatted_duration = f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"

            metadata: Dict[str, Any] = {
                "title": "Desconocido",
                "artist": "Desconocido",
                "album": "Desconocido",
                "duration": formatted_duration,
                "lyrics": []
            }

            try:
                id3 = ID3(file_path)
            except ID3NoHeaderError:
                id3 = None

            if id3:
                if "TIT2" in id3:
                    metadata["title"] = id3["TIT2"].text[0]
                if "TPE1" in id3:
                    metadata["artist"] = id3["TPE1"].text[0]
                if "TALB" in id3:
                    metadata["album"] = id3["TALB"].text[0]

                uslts = id3.getall("USLT")
                if uslts:
                    lyrics_crudo = "\n".join(u.text for u in uslts)
                    metadata["lyrics"] = self.formatear_Lyrics(lyrics_crudo)

                sylt_frames = id3.getall("SYLT")
                if sylt_frames and not metadata["lyrics"]:
                    for frame in sylt_frames:
                        for entry in getattr(frame, "text", []):
                            text = None
                            time_ms = None

                            if isinstance(entry, tuple) and len(entry) == 2:
                                a, b = entry
                                if isinstance(a, (int, float)):
                                    time_ms = int(a)
                                    text = b
                                elif isinstance(b, (int, float)):
                                    time_ms = int(b)
                                    text = a
                                else:
                                    text = str(a)
                                    time_ms = 0
                            else:
                                text = str(entry)
                                time_ms = 0

                            if isinstance(text, bytes):
                                try:
                                    text = text.decode("utf-8")
                                except Exception:
                                    text = text.decode("latin-1", errors="replace")

                            s = int(time_ms // 1000)
                            ms = int(time_ms % 1000)
                            timestamp = f"{s//60:02d}:{s%60:02d}.{ms:03d}"

                            metadata["lyrics"].append({
                                "ts": timestamp,
                                "lyrc": text.strip()
                            })

            return metadata
        except Exception:
            return {
                "title": "Desconocido",
                "artist": "Desconocido",
                "album": "Desconocido",
                "duration": "00:00:000",
                "lyrics": []
            }

    def formatear_Lyrics(self, lyrics_crudo):
        """
        Procesa las letras crudas provenientes de los metadatos y las formatea en una estructura limpia.
        :param lyrics_crudo: Texto crudo de las letras con marcas de tiempo.
        :return: Lista de diccionarios con las letras formateadas.
        """
        lyrics_limpio = []
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
        Escribe los metadatos en un archivo MP3.
        Actualmente, solo se admite la escritura de letras (USLT).
        """
        try:
            try:
                audio = ID3(file_path)
            except ID3NoHeaderError:
                audio = ID3()

            try:
                audio.delall("USLT")
                audio.delall("SYLT")
            except Exception:
                pass

            for frame in list(audio.getall("TXXX")):
                desc = (getattr(frame, "desc", "") or "").strip().lower()
                if "lyric" in desc or "unsynced" in desc or desc == "lrc":
                    try:
                        audio.delall(f"TXXX:{frame.desc}")
                    except Exception:
                        audio.delall("TXXX")

            for frame in list(audio.getall("COMM")):
                desc = (getattr(frame, "desc", "") or "").strip().lower()
                if "lyric" in desc or "unsynced" in desc or desc == "lrc":
                    try:
                        audio.delall("COMM")
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
                    audio.add(USLT(encoding=3, lang="eng", desc="Lyrics", text=lyrics_text))
                else:
                    print("Error: El campo 'lyrics' debe ser una lista de diccionarios.")
                    return False

            audio.save(file_path, v2_version=3)
            print(f"Letras sincronizadas guardadas correctamente en el archivo MP3: {file_path}")
            return True
        except Exception as e:
            print(f"Error al guardar las letras sincronizadas en el archivo MP3: {e}")
            return False





