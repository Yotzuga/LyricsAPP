# Lyrics Sync (PyQt6)

Aplicación de escritorio para sincronizar letras con audio.

Características principales
- Cargar canciones y mostrar letra en tabla con timestamps.
- Reproducir audio con libVLC (python-vlc).
- Asignar el tiempo actual del reproductor a marcadores vacíos (AsignarRowTime).
- Eliminar el último marcador asignado (BackSync).
- Doble clic en línea para hacer seek sin detener la reproducción.

Estructura
- `main.py` - punto de entrada y wiring de controladores.
- `controllers/` - controladores UI y servicios (LyricsController, PlayerController, TimesController, etc.).
- `player/` - wrapper VLC.
- `threads/` - hilo de actualización de tiempo.

Requisitos
- Python 3.8+
- PyQt6
- python-vlc

Instalación rápida (Windows PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Notas
- Asegúrate de tener VLC instalado y que python-vlc pueda encontrar libvlc.

## Licencia

Este proyecto está licenciado bajo la licencia MIT. Consulta el archivo <a>LICENSE</a> para más detalles.
