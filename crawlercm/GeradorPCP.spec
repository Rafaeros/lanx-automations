# GeradorPCP.spec
# Para gerar o executável:
#   pyinstaller GeradorPCP.spec

import os
from PyInstaller.utils.hooks import collect_submodules
import xlsxwriter

block_cipher = None

project_path = os.path.abspath(".")
core_path = os.path.join(project_path, "core")
services_path = os.path.join(project_path, "services")

xlsxwriter_path = os.path.dirname(xlsxwriter.__file__)

datas = [
    (core_path, "core"),
    (services_path, "services"),
    (os.path.join(project_path, ".env"), "."),
    (xlsxwriter_path, "xlsxwriter"),  # include entire xlsxwriter package
]

hiddenimports = (
    collect_submodules("core") +
    collect_submodules("services") +
    collect_submodules("pydantic") +
    collect_submodules("pydantic_settings") +
    collect_submodules("xlsxwriter")
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
    excludes=[
        'PyQt5', 
        'PyQt6', 
        'PySide2'
    ],  # evitando conflitos com PySide6
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
    console=False,
    icon='core/assets/images/icon.ico'
)

