# PyInstaller spec file for LyricsAPP
# Build with: pyinstaller build.spec

block_cipher = None

import PyInstaller.config

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = []

# PyQt6 plugins are handled automatically in recent PyInstaller, but you can force include if needed
# hiddenimports += collect_submodules('PyQt6')


a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('gui/LyricsGUI.ui', 'gui')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LyricsAPP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LyricsAPP'
)
