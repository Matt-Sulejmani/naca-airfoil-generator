# ✈ NACA Airfoil Generator

A clean, desktop GUI tool for generating **NACA 4-digit and 5-digit** airfoil profiles — with live preview and export to **CSV** and **STEP** formats compatible with Siemens NX, CATIA, SolidWorks, FreeCAD, and any other CAD package.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![CAD](https://img.shields.io/badge/Export-STEP%20%7C%20CSV-orange)

---

## Features

- **NACA 4-digit** (e.g. `2412`, `0012`, `4415`) and **5-digit** (e.g. `23012`) series
- Cosine-spaced point distribution for accurate leading/trailing edge resolution
- Live airfoil preview with camber line, thickness markers, and chord annotation
- **STEP export** — solid body, NX-ready (import via File → Import → STEP)
- **CSV export** — upper/lower surface coordinates with metadata header
- Geometric property panel: max thickness, t/c ratio, max camber, camber position
- Threaded STEP export (UI stays responsive)

---

## Screenshots

> _Add a screenshot of the GUI here after first run_

---

## Installation

```bash
git clone https://github.com/yourusername/naca-airfoil-generator.git
cd naca-airfoil-generator
pip install -r requirements.txt
python main.py
```

> **Note:** `cadquery` installation may take a minute — it bundles an Open CASCADE kernel.

### Requirements
- Python 3.10+
- numpy, matplotlib, cadquery (see `requirements.txt`)
- Tkinter (included with standard Python on Windows/macOS; on Linux: `sudo apt install python3-tk`)

---

## Usage

1. Enter a NACA code (4 or 5 digits) in the **NACA Code** field
2. Set your desired **chord length in mm**
3. Adjust **points per surface** (50–200 is typical)
4. Click **Generate** — the preview updates instantly
5. Export to **CSV** or **STEP** via the export buttons

### Importing into Siemens NX
1. Export as `.step`
2. In NX: **File → Import → Step214** (or Step203)
3. The airfoil appears as a solid body in the XY plane
4. Use **Transform** or **Move Object** to position it in your assembly

---

## NACA Code Reference

| Code | Meaning |
|------|---------|
| `2412` | 2% camber, max camber at 40% chord, 12% thick |
| `0012` | Symmetric, 12% thick |
| `23012` | 5-digit, 12% thick, high-lift camber |
| `4415` | 4% camber, 40% chord, 15% thick |

---

## Project Structure

```
naca-airfoil-generator/
├── airfoil/
│   ├── geometry.py    # NACA 4 & 5 digit math
│   ├── exporter.py    # CSV + STEP export
│   └── plotter.py     # Matplotlib preview
├── gui/
│   └── app.py         # Tkinter GUI
├── main.py            # Entry point
├── requirements.txt
├── LICENSE
└── README.md
```

---

## License

MIT — free to use, modify, and distribute. See [LICENSE](LICENSE).

---

## Contributing

PRs welcome! Potential extensions:
- XFOIL/OpenFOAM mesh export
- Cp distribution plot
- Bezier/custom airfoil support
- Batch export for multiple profiles

---

*Built by an aerospace engineering student. If this saved you time, consider starring the repo ⭐*
