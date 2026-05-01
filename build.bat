@echo off
REM build.bat — local build helper for NACA Airfoil Generator (Windows)
REM Run this in a terminal to produce a local dist\ folder.
REM For release builds, push a git tag and let GitHub Actions handle it.

echo === NACA Airfoil Generator - Local Build ===
echo.

REM Check Python
python --version || (echo Python not found && exit /b 1)

REM Install dependencies
echo [1/3] Installing dependencies...
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet

REM Run PyInstaller
echo [2/3] Running PyInstaller...
pyinstaller naca_airfoil.spec --noconfirm

REM Report
echo.
echo [3/3] Build complete!
echo Output: dist\NACA_Airfoil_Generator\
echo.
echo To run: dist\NACA_Airfoil_Generator\NACA_Airfoil_Generator.exe
pause
