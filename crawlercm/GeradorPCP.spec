# GeradorPCP.spec
# Para gerar:
#   pyinstaller GeradorPCP.spec

import os
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

project_path = os.path.abspath(".")
core_path = os.path.join(project_path, "core")
services_path = os.path.join(project_path, "services")

datas = [
    (core_path, "core"),          # inclui pasta core inteira
    (services_path, "services"),  # inclui pasta services inteira
    (os.path.join(project_path, ".env"), "."),  # inclui .env na raiz
]

hiddenimports = (
    collect_submodules("core") +
    collect_submodules("services") +
    collect_submodules("pydantic") +
    collect_submodules("pydantic_settings")
)

a = Analysis(
    ['main.py'],
    pathex=[project_path],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PyQt6', 'PySide2'],  # exclui se você estiver usando PySide6
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
    icon='core/assets/images/icon.ico'
)
