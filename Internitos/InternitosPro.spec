# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['Internitos/main.py'],  # Asegúrate que esta ruta sea correcta relativa a donde corres pyinstaller
    pathex=[],
    binaries=[],
    datas=[
        ('Internitos/data', 'data'), 
        ('Internitos/assets', 'assets')
    ],
    # AÑADIDO: cryptography es crucial para que funcione el directorio compilado
    hiddenimports=['flet', 'cryptography'], 
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
    name='InternitosPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, # Ponlo en True si quieres ver errores al debuggear
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Internitos/assets/icon.ico', # Uso de barra normal para evitar escapes
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='InternitosPro',
)