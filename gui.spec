# -*- mode: python ; coding: utf-8 -*-

import sys
import os


SPEC_DIR = os.path.abspath(SPECPATH)

if sys.platform == "win32":
    icon_file = os.path.join(SPEC_DIR, "assets", "c8.ico")
elif sys.platform == "darwin":
    icon_file = os.path.join(SPEC_DIR, "assets", "c8.icns")
else:
    icon_file = None

a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/c8.png', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='HelloCHIP',
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
    icon=icon_file
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='HelloCHIP',
)
