#!/usr/bin/env bash
# build.sh — local build helper for NACA Airfoil Generator
# Run this on your machine to produce a local dist/ folder.
# For release builds, push a git tag and let GitHub Actions handle it.

set -e

echo "=== NACA Airfoil Generator — Local Build ==="
echo ""

# Check Python
python3 --version || { echo "Python 3 not found"; exit 1; }

# Install / upgrade dependencies
echo "[1/3] Installing dependencies..."
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet

# Run PyInstaller
echo "[2/3] Running PyInstaller..."
pyinstaller naca_airfoil.spec --noconfirm

# Report
echo ""
echo "[3/3] Build complete!"
echo "Output: dist/NACA_Airfoil_Generator/"
echo ""

# Quick size report
du -sh dist/NACA_Airfoil_Generator/ 2>/dev/null || true
echo ""
echo "To run: ./dist/NACA_Airfoil_Generator/NACA_Airfoil_Generator"
