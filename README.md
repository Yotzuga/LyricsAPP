# LyricsAPP

Aplicación de escritorio para Windows que permite reproducir música, visualizar y sincronizar letras, y escribirlas en los metadatos del archivo. Está construida con PyQt6, reproduce con VLC (vía python-vlc) y usa Mutagen para leer/escribir metadatos en MP3/FLAC/M4A.

## Características
- Reproducción de audio mediante VLC (estable y compatible con múltiples formatos).
- Extracción de metadatos con Mutagen: título, artista, álbum, duración, letras (USLT/SYLT, FLAC tags, MP4).
- Visualización y edición de letras; sincronización por marcas de tiempo.
- Guardado de letras en los propios archivos (MP3/FLAC/M4A) sin herramientas externas.
- Interfaz moderna con PyQt6.

## Requisitos (usuarios finales)
- Windows 10/11 (64 bits)
- VLC 64 bits instalado en el sistema
	- Descarga: https://www.videolan.org/vlc/
	- Instálalo en la ruta por defecto (p. ej. `C:\\Program Files\\VideoLAN\\VLC`).

## Uso básico
- Importa o abre tu biblioteca de música.
- Carga un archivo (MP3/FLAC/M4A), reproduce y edita/sincroniza las letras.
- Guarda para escribir las letras dentro del propio archivo de audio.

## Hotkeys
- Espacio: Play/Pausa
- Ctrl + S: Guardar letras
- Ctrl + B: Abrir biblioteca
- N: Eliminar marca de tiempo seleccionada
- M: Asignar marca de tiempo actual

## Desarrollo (desde código fuente)
Requisitos: Python 3.12 o 3.13 y VLC instalado.

1) Crear y activar un entorno virtual (PowerShell):
```powershell
py -3 -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

2) Ejecutar la app:
```powershell
python .\\main.py
```

Si VLC no está en la ruta por defecto, puedes exportar temporalmente las variables (opcional):
```powershell
$env:VLC_PATH = "C:\\Program Files\\VideoLAN\\VLC"
$env:VLC_PLUGIN_PATH = "$env:VLC_PATH\\plugins"
python .\\main.py
```

## Construir ejecutable (.exe)
Opción sencilla (onefile):
```powershell
pyinstaller --name LyricsAPP --noconsole --onefile --add-data 'gui\\LyricsGUI.ui;gui' main.py
```
El binario quedará en `dist/LyricsAPP.exe`.

También dispones de un script de ayuda:
```powershell
./build.ps1 -OneFile
```

## Crear instalador (Inno Setup)
1) Genera previamente el ejecutable (ver sección anterior).
2) Abre y compila `installer.iss` con Inno Setup Compiler.
3) Obtendrás `Output/LyricsAPP-Setup.exe`.

Este instalador muestra un aviso previo indicando el requisito de VLC.

## Estructura del proyecto
- `main.py`: arranque de la app y carga de `gui/LyricsGUI.ui`.
- `controllers/`: lógica de UI (biblioteca, letras, player, tiempos, importación).
- `metadata/`: extractores/editores de metadatos para MP3, FLAC y M4A (Mutagen).
- `player/`: wrapper de VLC (python-vlc) y entidad `Song`.
- `gui/`: recursos de UI (archivo .ui de Qt Designer).
- `threads/`: hilos auxiliar(es) para actualizar tiempo de reproducción.
- `utils/`: utilidades varias (biblioteca, etc.).

## Solución de problemas
- VLC no encontrado / reproducción falla:
	- Asegúrate de tener VLC 64 bits instalado en `C:\\Program Files\\VideoLAN\\VLC`.
	- Si usas consola: exporta temporalmente `VLC_PATH` y `VLC_PLUGIN_PATH` como en el ejemplo de arriba.
	- Desajuste de arquitectura: Python/EXE x64 requieren VLC x64.
- Error al activar venv (ExecutionPolicy):
	- Ejecuta solo para esa sesión: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` y vuelve a activar.
- Mutagen no puede escribir:
	- Verifica permisos del archivo, que no esté en uso y que el formato sea MP3/FLAC/M4A.

## Créditos y licencias
- VLC es un producto de VideoLAN (https://www.videolan.org/). Este proyecto usa `python-vlc` como binding.
- Mutagen: https://mutagen.readthedocs.io/
- PyQt6: https://pypi.org/project/PyQt6/

© 2025. Todos los derechos reservados.
