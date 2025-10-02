# Project2 - LyricsAPP

Este proyecto es una aplicación PyQt6 para gestionar y sincronizar letras de canciones, con reproducción basada en VLC y extracción/edición de metadatos con mutagen.

## Requisitos
- Python 3.12 o 3.13 (recomendado)
- Windows 10/11

## Crear y activar un entorno virtual (Windows PowerShell)

1. Crear el entorno virtual en la carpeta del proyecto:
```powershell
py -3 -m venv .venv
```

2. Activar el entorno virtual:
```powershell
.\.venv\Scripts\Activate.ps1
```

3. Actualizar pip (opcional pero recomendado):
```powershell
python -m pip install --upgrade pip
```

4. Instalar dependencias:
```powershell
pip install -r requirements.txt
```

## Ejecutar la aplicación

Desde el directorio `Project2` (con el entorno activado):
```powershell
python .\main.py
```

## Notas sobre VLC
- El paquete `python-vlc` es un binding. Necesitas el reproductor VLC instalado para tener la librería nativa.
- Descarga VLC para Windows desde: https://www.videolan.org/vlc/
- Instala la versión de 64 bits si tu Python es de 64 bits. Asegúrate de que VLC quede en el PATH o en su ruta por defecto (por ejemplo, `C:\Program Files\VideoLAN\VLC`).

## Problemas comunes
- "ModuleNotFoundError: No module named 'PyQt6'" -> Activa el entorno virtual y ejecuta `pip install -r requirements.txt`.
- "NameError: name 'vlc' is not defined" o fallos al reproducir -> Asegúrate de tener VLC instalado en el sistema.
- Errores de mutagen al escribir tags -> Comprueba que el archivo no esté protegido y que el formato sea el soportado (MP3/FLAC/M4A).
