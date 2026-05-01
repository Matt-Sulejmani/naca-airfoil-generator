# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec file for NACA Airfoil Generator
#
# Build locally:
#   pyinstaller naca_airfoil.spec
#
# Output: dist/NACA_Airfoil_Generator   (folder mode — recommended for cadquery)
#
# Note: cadquery bundles Open CASCADE which is large (~150 MB).
# One-folder mode keeps startup fast; one-file mode is slower to launch.

import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect everything cadquery needs (OCC kernel + its data files)
cq_datas, cq_binaries, cq_hiddenimports = collect_all("cadquery")
ocp_datas, ocp_binaries, ocp_hiddenimports = collect_all("OCP")

# Matplotlib needs its backends and data files
mpl_datas, mpl_binaries, mpl_hiddenimports = collect_all("matplotlib")

all_datas    = cq_datas    + ocp_datas    + mpl_datas
all_binaries = cq_binaries + ocp_binaries + mpl_binaries
all_hidden   = (
    cq_hiddenimports
    + ocp_hiddenimports
    + mpl_hiddenimports
    + collect_submodules("cadquery")
    + collect_submodules("OCP")
    + [
        "tkinter",
        "tkinter.ttk",
        "tkinter.filedialog",
        "tkinter.messagebox",
        "numpy",
        "matplotlib.backends.backend_tkagg",
        "matplotlib.backends._backend_tk",
    ]
)

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=all_binaries,
    datas=all_datas,
    hiddenimports=all_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Trim unused heavy packages
        "scipy", "pandas", "PIL", "cv2",
        "IPython", "jupyter", "notebook",
        "test", "unittest",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,          # folder mode (faster startup, smaller RAM)
    name="NACA_Airfoil_Generator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                       # compress binaries where possible
    console=False,                  # no terminal window on Windows
    disable_windowed_traceback=False,
    # icon="assets/icon.ico",       # uncomment once you add an icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="NACA_Airfoil_Generator",
)
