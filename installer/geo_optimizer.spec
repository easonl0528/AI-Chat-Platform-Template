# PyInstaller spec file to bundle the GEO optimizer backend + frontend into an EXE.
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

datas = collect_data_files(
    "geo_optimizer",
    includes=["static/*.html", "static/*.js", "static/*.css", "static/*/*"],
)
gitkeep = Path(__file__).resolve().parent.parent / "geo_data" / ".gitkeep"
if gitkeep.exists():
    datas.append((str(gitkeep), "geo_data"))

hiddenimports = []


a = Analysis(
    ['server.py'],
    pathex=[],
    binaries=[],
    datas=datas,
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
    name='geo-optimizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
    name='geo-optimizer'
)
