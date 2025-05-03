# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['server2.py'],
    pathex=[],
    binaries=[],
    datas=[('browzee_agent/agent/system_prompt.md', 'browzee_agent/agent'), ('browzee_agent/dom/buildDomTree.js', 'browzee_agent/dom')],
    hiddenimports=['pydantic', 'playwright', 'PIL', 'posthog', 'PIL.Image', 'selenium', 'pydantic-core', 'pydantic.deprecated.decorator'],
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
    a.binaries,
    a.datas,
    [],
    name='server2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
