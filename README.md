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
- `controllers/` - controladores UI y servicios.
- `player/` - wrapper VLC y clase `Song`.
- `threads/` - hilo de actualización de tiempo.

Requisitos
- Python 3.8+
- PyQt6
- python-vlc

Dependencias recomendadas
- mutagen (lectura de metadata de audio)
- pyinstaller (si quieres generar un ejecutable .exe)

Versión de Python recomendada
- Esta aplicación se ha probado con Python 3.10, 3.11, 3.12 y 3.13.
- Recomendamos usar Python 3.10–3.13 para evitar incompatibilidades con PyInstaller/PyQt6 y python-vlc.

Comprobar versión de Python (PowerShell / terminal):
```powershell
python --version
# o dentro de Python
python -c "import sys; print(sys.version)"
```

Instalación rápida (Windows PowerShell)

```powershell
# Sitúate en la carpeta del proyecto (ajusta la ruta a la ubicación en tu equipo)
Set-Location '<ruta-a-tu-proyecto>\Project2'

python -m venv .venv
# Si PowerShell bloquea la activación por políticas, ejecutar sólo para la sesión actual:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

Cómo crear un ejecutable con PyInstaller (recomendado empezar con `--onedir`)

```powershell
# compilar y añadir el archivo UI para que uic.loadUi lo encuentre en runtime
pyinstaller --noconfirm --clean --onedir --windowed --name LyricsAPP --add-data "gui\LyricsGUI.ui;gui" main.py

# si quieres ver errores en consola mientras depuras, usa --console en lugar de --windowed
pyinstaller --noconfirm --clean --onedir --console --name LyricsAPP --add-data "gui\LyricsGUI.ui;gui" main.py
```

Notas y solución de problemas

- Arquitectura: asegúrate de usar Python de la misma arquitectura (32/64-bit) que tu instalación de VLC — python-vlc requiere que libvlc sea compatible con Python.
- Si el exe falla por falta de `LyricsGUI.ui`, añade `--add-data "gui\LyricsGUI.ui;gui"` (como en el ejemplo) o incluye el archivo en el `.spec`.
- Si hay problemas de reproducción o faltan codecs/libvlc, copia la carpeta `plugins` de tu instalación de VLC (ej.: `C:\Program Files\VideoLAN\VLC\plugins`) dentro de `dist\LyricsAPP` junto al exe, o incluye esa carpeta directamente en el `.spec` con `Tree()`.

Empaquetado para distribución
- La forma más sencilla de distribuir es crear un ZIP de `dist\LyricsAPP` y compartirlo. Para crear un instalador puedes usar Inno Setup o NSIS.

Contacto / Desarrollo
- Si quieres, puedo ayudarte a: añadir logging a `main.py`, ajustar el `.spec` para incluir libvlc/plugins automáticamente, o generar un script de Inno Setup.

---

Archivo `requirements.txt` recomendado contiene las dependencias principales y opcionales para build.

