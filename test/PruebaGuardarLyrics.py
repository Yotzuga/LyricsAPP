import sys
import os

# Agregar el directorio raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from metadata.FLACMetadataExtractor import FLACMetadataExtractor

def test_metadata_extraction():
    # Ejemplo: solo FLAC
    test_file = "C:\\Users\\USER\\Documents\\visual-studio-code\\sontest\\01.ReawakeR (feat.Felix of Stray Kids).flac"
    extractor = FLACMetadataExtractor()
    try:
        metadata = extractor.extract_metadata(test_file)
        print(f"Metadatos extraídos para {test_file}:")
        print(f"Título: {metadata['title']}")
        print(f"Artista: {metadata['artist']}")
        print(f"Álbum: {metadata['album']}")
        print(f"Duración: {metadata['duration']}")
        print("Letras:")
        for lyric in metadata["lyrics"]:
            print(f"[{lyric['ts']}] {lyric['lyrc']}")
    except Exception as e:
        print(f"Error al extraer metadatos para {test_file}: {e}")

def get_user_metadataLyrics():
    return {
        "lyrics": [
            {"ts": "02:43.170", "lyrc": "もうすぐ何か見えるだろうと"},
            {"ts": "02:43.170", "lyrc": "mo sugu nanika mieru darou to"},
            {"ts": "02:46.090", "lyrc": "息を止めるの今"},
            {"ts": "02:46.090", "lyrc": "iki wo tomeru no ima"},
            {"ts": "02:50.730", "lyrc": "も一回、も一回"},
            {"ts": "02:50.730", "lyrc": "mo ikkai, mo ikkai"},
            {"ts": "02:52.970", "lyrc": "私をどうか転がしてと"},
            {"ts": "02:52.970", "lyrc": "watashi wo douka korogashite to"},
            {"ts": "02:55.410", "lyrc": "少女は言う、少女は言う"},
            {"ts": "02:55.410", "lyrc": "shoujo wa iu, shoujo wa iu"},
            {"ts": "02:58.080", "lyrc": "言葉に笑みを奏でながら"},
            {"ts": "02:58.080", "lyrc": "kotoba ni emi wo kanade nagara"},
            {"ts": "03:00.590", "lyrc": "もいいかい"},
            {"ts": "03:00.590", "lyrc": "mo ii kai"},
            {"ts": "03:01.690", "lyrc": "もういいよ"},
            {"ts": "03:01.690", "lyrc": "mo ii yo"},
            {"ts": "03:02.860", "lyrc": "そろそろ君も疲れたろうね"},
            {"ts": "03:02.860", "lyrc": "sorosoro kimi mo tsukareta rounene"},
            {"ts": "03:05.680", "lyrc": "息をやめる今"},
            {"ts": "03:05.680", "lyrc": "iki wo yameru ima"}
        ]
    }

def test_write_metadata():
    test_file = "C:\\Users\\USER\\Documents\\visual-studio-code\\sontest\\01.ReawakeR (feat.Felix of Stray Kids).flac"
    metadataLyrics = get_user_metadataLyrics()
    extractor = FLACMetadataExtractor()
    success = extractor.write_metadata(test_file, metadataLyrics)
    if success:
        print(f"Letras actualizadas correctamente en el archivo: {test_file}")
    else:
        print(f"Error al actualizar las letras en el archivo: {test_file}")

if __name__ == "__main__":
    test_metadata_extraction()
    test_write_metadata()
    test_metadata_extraction()

