# Build script for LyricsAPP on Windows (PowerShell)
# Usage: .\build.ps1 [-OneFile]

param(
    [switch]$OneFile
)

# Ensure venv
if (-not (Test-Path .\.venv)) {
    py -3 -m venv .venv
}
. .\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install pyinstaller -r requirements.txt

# PyInstaller options
$common = @('main.py', '--name', 'LyricsAPP', '--noconsole', '--add-data', 'gui/LyricsGUI.ui;gui')
if ($OneFile) {
    $common += '--onefile'
}

# VLC runtime note: the app usa python-vlc que requiere VLC instalado en el sistema.
pyinstaller @common

Write-Host "Build listo en ./dist/LyricsAPP"
