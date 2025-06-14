# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['graf_csv.py'],
    pathex=[],
    binaries=[],
    datas=[],    hiddenimports=[
        'tkinter',
        'tkinter.filedialog',
        'tkinter.ttk',
        'tkinter.messagebox',
        'pandas',
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.dates',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.backends._backend_tkagg',
        'matplotlib.widgets',
        'numpy',
        'openpyxl',
        'xlrd',
        'webbrowser',
        'datetime',
        'PIL._tkinter_finder'
    ],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Multi-Parameter_Data_Analyzer_v1.1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Отключаем UPX для стабильности
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Отключаем консоль для GUI приложения
    disable_windowed_traceback=False,
    argv_emulation=False,    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None  # Можно добавить иконку позже
)
