# GeradorPCP.spec
# Para build: pyinstaller GeradorPCP.spec

import os
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

project_path = os.path.abspath(".")

datas = [
    ('core/assets', 'core/assets'),
    ('core/frontend/widgets', 'core/frontend/widgets'),
    ('core/utils', 'core/utils'),
    ('services', 'services'),
]

hiddenimports = (
    collect_submodules('core') +
    collect_submodules('services')
)

a = Analysis(
    ['main.py'],
    pathex=[project_path],
    datas=datas,
    hiddenimports=hiddenimports,
    binaries=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],

    # AQUI ESTÁ O IMPORTANTE!!!
    excludes=['PyQt5', 'PyQt6', 'PySide2'],

    cipher=block_cipher
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GeradorPCP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False
)
