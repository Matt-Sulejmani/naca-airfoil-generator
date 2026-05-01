"""
NACA Airfoil Geometry Generator
Supports NACA 4-digit and 5-digit series.

MIT License - Copyright (c) 2025
"""

import numpy as np


def _cosine_spacing(n: int) -> np.ndarray:
    """Generate cosine-spaced parameter from 0 to 1 for better LE/TE resolution."""
    beta = np.linspace(0, np.pi, n)
    return (1 - np.cos(beta)) / 2


def naca4(code: str, n_points: int = 100, chord: float = 1.0):
    """
    Generate NACA 4-digit airfoil coordinates.

    Parameters
    ----------
    code      : 4-character string, e.g. '2412'
    n_points  : number of points per surface (upper/lower)
    chord     : chord length in mm

    Returns
    -------
    xu, yu, xl, yl : upper and lower surface x/y coordinates (numpy arrays)
    """
    if len(code) != 4 or not code.isdigit():
        raise ValueError(f"Invalid NACA 4-digit code: '{code}'")

    m = int(code[0]) / 100        # max camber
    p = int(code[1]) / 10         # location of max camber
    t = int(code[2:]) / 100       # max thickness

    x = _cosine_spacing(n_points)

    # Thickness distribution (NACA standard)
    yt = (t / 0.2) * (
        0.2969 * np.sqrt(x)
        - 0.1260 * x
        - 0.3516 * x**2
        + 0.2843 * x**3
        - 0.1015 * x**4
    )

    # Camber line and gradient
    yc = np.where(
        x < p,
        (m / p**2) * (2 * p * x - x**2) if p > 0 else np.zeros_like(x),
        (m / (1 - p)**2) * ((1 - 2 * p) + 2 * p * x - x**2) if p > 0 else np.zeros_like(x),
    )
    dyc_dx = np.where(
        x < p,
        (2 * m / p**2) * (p - x) if p > 0 else np.zeros_like(x),
        (2 * m / (1 - p)**2) * (p - x) if p > 0 else np.zeros_like(x),
    )

    theta = np.arctan(dyc_dx)

    xu = (x - yt * np.sin(theta)) * chord
    yu = (yc + yt * np.cos(theta)) * chord
    xl = (x + yt * np.sin(theta)) * chord
    yl = (yc - yt * np.cos(theta)) * chord

    return xu, yu, xl, yl


def naca5(code: str, n_points: int = 100, chord: float = 1.0):
    """
    Generate NACA 5-digit airfoil coordinates.

    Parameters
    ----------
    code      : 5-character string, e.g. '23012'
    n_points  : number of points per surface
    chord     : chord length in mm

    Returns
    -------
    xu, yu, xl, yl : upper and lower surface x/y coordinates (numpy arrays)
    """
    if len(code) != 5 or not code.isdigit():
        raise ValueError(f"Invalid NACA 5-digit code: '{code}'")

    # Standard NACA 5-digit camber line lookup
    # First digit * 0.15 / 2 = design CL, second+third = 2*p (max camber pos)
    cl_design = int(code[0]) * 3 / 20
    p_code = int(code[1:3])
    t = int(code[3:]) / 100

    # Proper coefficients from NACA Report 824
    camber_params = {
        10: (0.05800, 361.4),
        20: (0.12600, 51.645),
        30: (0.20250, 15.957),
        40: (0.29000, 6.643),
        50: (0.39100, 3.230),
    }

    if p_code not in camber_params:
        raise ValueError(f"Unsupported NACA 5-digit camber designation: {p_code}. Use 10,20,30,40,50.")

    p, k1 = camber_params[p_code]
    r = p  # alias

    x = _cosine_spacing(n_points)
    t_val = t

    # Thickness (same as 4-digit)
    yt = (t_val / 0.2) * (
        0.2969 * np.sqrt(x)
        - 0.1260 * x
        - 0.3516 * x**2
        + 0.2843 * x**3
        - 0.1015 * x**4
    )

    # Camber line
    yc = np.where(
        x <= r,
        (k1 / 6) * (x**3 - 3 * r * x**2 + r**2 * (3 - r) * x),
        (k1 * r**3 / 6) * (1 - x),
    )
    dyc_dx = np.where(
        x <= r,
        (k1 / 6) * (3 * x**2 - 6 * r * x + r**2 * (3 - r)),
        -(k1 * r**3 / 6),
    )

    theta = np.arctan(dyc_dx)

    xu = (x - yt * np.sin(theta)) * chord
    yu = (yc + yt * np.cos(theta)) * chord
    xl = (x + yt * np.sin(theta)) * chord
    yl = (yc - yt * np.cos(theta)) * chord

    return xu, yu, xl, yl


def generate_airfoil(code: str, n_points: int = 100, chord: float = 1.0):
    """
    Dispatch to the correct NACA generator based on code length.

    Returns
    -------
    xu, yu, xl, yl, info_dict
    """
    code = code.strip().upper()
    if len(code) == 4:
        xu, yu, xl, yl = naca4(code, n_points, chord)
        info = {
            "series": "NACA 4-digit",
            "code": code,
            "max_camber_pct": int(code[0]),
            "max_camber_pos_pct": int(code[1]) * 10,
            "thickness_pct": int(code[2:]),
            "chord_mm": chord,
            "n_points": n_points,
        }
    elif len(code) == 5:
        xu, yu, xl, yl = naca5(code, n_points, chord)
        info = {
            "series": "NACA 5-digit",
            "code": code,
            "thickness_pct": int(code[3:]),
            "chord_mm": chord,
            "n_points": n_points,
        }
    else:
        raise ValueError("Only NACA 4-digit and 5-digit codes are supported.")

    return xu, yu, xl, yl, info


def get_properties(xu, yu, xl, yl, chord):
    """Compute basic geometric properties of the airfoil."""
    # Max thickness and location
    thickness = yu - np.interp(xu, xl, yl)
    max_t_idx = np.argmax(thickness)
    max_thickness = thickness[max_t_idx]
    max_t_location = xu[max_t_idx]

    # Max camber
    yc = (yu + np.interp(xu, xl, yl)) / 2
    max_camber_idx = np.argmax(np.abs(yc))
    max_camber = yc[max_camber_idx]

    return {
        "max_thickness_mm": round(float(max_thickness), 4),
        "max_thickness_pct_chord": round(float(max_thickness / chord * 100), 2),
        "max_thickness_location_mm": round(float(max_t_location), 4),
        "max_camber_mm": round(float(max_camber), 4),
        "max_camber_pct_chord": round(float(max_camber / chord * 100), 2),
    }
