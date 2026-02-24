import os
import platform
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

is_windows = platform.system().lower().startswith("win")

project_path = os.path.abspath(".")
core_path = os.path.join(project_path, "core")
datas = [
    (core_path, "core"),
]

env_path = os.path.join(project_path, ".env")
if os.path.exists(env_path):
    datas.append((env_path, "."))

hiddenimports = (
    collect_submodules("core") +
    collect_submodules("qasync") +
    collect_submodules("PySide6")
)

if is_windows:
    hiddenimports.extend(["win32print", "win32api"])

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
        'PySide2',
        'xlsxwriter' # Removi o xlsxwriter do antigo, caso não use neste projeto
    ],  
    cipher=block_cipher
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

icon_path = 'core/assets/icon.png'
if is_windows and os.path.exists('core/assets/icon.ico'):
    icon_path = 'core/assets/icon.ico'

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GeradorEtiquetas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=icon_path
)