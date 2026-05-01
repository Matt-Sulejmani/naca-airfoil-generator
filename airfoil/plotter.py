"""
Airfoil Preview Plotter — embeds in Tkinter via FigureCanvasTkAgg.

MIT License - Copyright (c) 2025
"""

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch


DARK_BG   = "#1a1a2e"
GRID_COL  = "#2a2a4a"
UPPER_COL = "#4fc3f7"   # sky blue — upper surface
LOWER_COL = "#81d4fa"   # lighter blue — lower surface
CAMBER_COL= "#ffd54f"   # amber — camber line
TEXT_COL  = "#e0e0e0"
ACCENT    = "#ff6b6b"


def build_figure() -> Figure:
    """Return a pre-styled Figure ready for embedding."""
    fig = Figure(figsize=(7, 3.2), dpi=100, facecolor=DARK_BG)
    ax = fig.add_subplot(111)
    ax.set_facecolor(DARK_BG)
    ax.tick_params(colors=TEXT_COL, labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COL)
    ax.grid(True, color=GRID_COL, linewidth=0.5, linestyle="--")
    ax.set_aspect("equal")
    ax.set_title("Airfoil Preview", color=TEXT_COL, fontsize=10, pad=8)
    ax.set_xlabel("x (mm)", color=TEXT_COL, fontsize=8)
    ax.set_ylabel("y (mm)", color=TEXT_COL, fontsize=8)
    fig.tight_layout(pad=1.5)
    return fig


def plot_airfoil(fig: Figure, xu, yu, xl, yl, info: dict, props: dict):
    """
    Draw the airfoil on the given Figure.

    Clears previous artists and redraws.
    """
    fig.clear()
    ax = fig.add_subplot(111)
    ax.set_facecolor(DARK_BG)
    ax.tick_params(colors=TEXT_COL, labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COL)
    ax.grid(True, color=GRID_COL, linewidth=0.5, linestyle="--")
    ax.set_aspect("equal")

    chord = info.get("chord_mm", 1.0)
    code  = info.get("code", "")
    series = info.get("series", "NACA")

    # Upper and lower surfaces
    ax.plot(xu, yu, color=UPPER_COL, linewidth=1.8, label="Upper surface")
    ax.plot(xl, yl, color=LOWER_COL, linewidth=1.8, label="Lower surface")

    # Close trailing edge
    ax.plot([xu[-1], xl[-1]], [yu[-1], yl[-1]], color=TEXT_COL, linewidth=1.0, linestyle=":")

    # Camber line
    yc = (yu + np.interp(xu, xl[::-1], yl[::-1])) / 2
    ax.plot(xu, yc, color=CAMBER_COL, linewidth=1.0, linestyle="--", label="Camber line", alpha=0.8)

    # Chord arrow
    ax.annotate(
        "", xy=(chord, 0), xytext=(0, 0),
        arrowprops=dict(arrowstyle="<->", color=ACCENT, lw=1.2),
    )
    ax.text(chord / 2, -props["max_thickness_mm"] * 0.9,
            f"c = {chord:.1f} mm", color=ACCENT, fontsize=7.5, ha="center")

    # Max thickness marker
    mt_x = props["max_thickness_location_mm"]
    mt_y = np.interp(mt_x, xu, yu)
    mt_y_l = np.interp(mt_x, xl, yl)
    ax.annotate("", xy=(mt_x, mt_y_l), xytext=(mt_x, mt_y),
                arrowprops=dict(arrowstyle="<->", color="#a5d6a7", lw=1.0))

    # Title & legend
    ax.set_title(f"{series}  {code}", color=TEXT_COL, fontsize=10, pad=6, fontweight="bold")
    ax.set_xlabel("x (mm)", color=TEXT_COL, fontsize=8)
    ax.set_ylabel("y (mm)", color=TEXT_COL, fontsize=8)
    leg = ax.legend(fontsize=7, loc="upper right",
                    facecolor=DARK_BG, edgecolor=GRID_COL, labelcolor=TEXT_COL)

    fig.tight_layout(pad=1.5)
