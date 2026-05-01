"""
NACA Airfoil Generator — Tkinter GUI
=====================================
Main application window. Provides inputs for NACA code, chord length,
and point count; live preview; and CSV / STEP export.

MIT License - Copyright (c) 2025
"""
# ── Imports and dependencies ──────────────────────────────────────────────────────────────────────
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from airfoil.geometry import generate_airfoil, get_properties
from airfoil.exporter import export_csv, export_step
from airfoil.plotter  import build_figure, plot_airfoil

# ── Styling for components ────────────────────────────────────────────────────────────────────────
BG        = "#1a1a2e"
BG2       = "#16213e"
BG3       = "#0f3460"
ACCENT    = "#4fc3f7"
ACCENT2   = "#ffd54f"
SUCCESS   = "#81c784"
ERR       = "#ef9a9a"
TEXT      = "#e0e0e0"
TEXT_DIM  = "#90a4ae"
BTN_HOVER = "#0288d1"

FONT_HEAD = ("Helvetica", 13, "bold")
FONT_BODY = ("Helvetica", 10)
FONT_MONO = ("Courier", 10)
FONT_SM   = ("Helvetica", 8)


class ToolTip:
    """Simple hover tooltip."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tw = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(self.tw, text=self.text, background="#263238",
                       foreground=TEXT, relief="solid", borderwidth=1,
                       font=FONT_SM, padx=6, pady=3)
        lbl.pack()

    def hide(self, _):
        if self.tw:
            self.tw.destroy()
            self.tw = None


class StyledButton(tk.Button):
    def __init__(self, master, **kwargs):
        color = kwargs.pop("color", ACCENT)
        super().__init__(
            master,
            bg=color, fg=BG, activebackground=BTN_HOVER,
            activeforeground="white", relief="flat",
            font=("Helvetica", 10, "bold"),
            padx=14, pady=6, cursor="hand2",
            **kwargs,
        )
        self.bind("<Enter>", lambda e: self.config(bg=BTN_HOVER, fg="white"))
        self.bind("<Leave>", lambda e: self.config(bg=color, fg=BG))


class PropertiesPanel(tk.Frame):
    """Right-side panel showing computed airfoil properties."""

    LABELS = [
        ("Max Thickness",     "max_thickness_mm",         "mm"),
        ("t/c",               "max_thickness_pct_chord",  "%"),
        ("Thickness at",      "max_thickness_location_mm","mm"),
        ("Max Camber",        "max_camber_mm",            "mm"),
        ("Camber ratio",      "max_camber_pct_chord",     "%"),
    ]

    def __init__(self, master, **kwargs):
        super().__init__(master, bg=BG2, **kwargs)
        tk.Label(self, text="Geometric Properties", font=FONT_HEAD,
                 bg=BG2, fg=ACCENT2).pack(anchor="w", padx=12, pady=(12, 6))
        self._vars = {}
        for label, key, unit in self.LABELS:
            row = tk.Frame(self, bg=BG2)
            row.pack(fill="x", padx=12, pady=2)
            tk.Label(row, text=label, font=FONT_SM, bg=BG2,
                     fg=TEXT_DIM, width=18, anchor="w").pack(side="left")
            var = tk.StringVar(value="—")
            self._vars[key] = var
            tk.Label(row, textvariable=var, font=FONT_MONO, bg=BG2,
                     fg=TEXT, anchor="e").pack(side="right")
            tk.Label(row, text=unit, font=FONT_SM, bg=BG2,
                     fg=TEXT_DIM).pack(side="right", padx=(0, 4))

    def update(self, props: dict):
        for key, var in self._vars.items():
            val = props.get(key, "—")
            var.set(f"{val:.4f}" if isinstance(val, float) else str(val))

    def clear(self):
        for var in self._vars.values():
            var.set("—")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NACA Airfoil Generator")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(900, 580)

        self._xu = self._yu = self._xl = self._yl = None
        self._info = self._props = None

        self._build_ui()
        self.after(200, self._generate)   # auto-generate default on startup

    # ── UI construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header bar ──
        header = tk.Frame(self, bg=BG3, pady=10)
        header.pack(fill="x")
        tk.Label(header, text="✈  NACA Airfoil Generator",
                 font=("Helvetica", 16, "bold"), bg=BG3, fg=ACCENT).pack(side="left", padx=18)
        tk.Label(header, text="NX-compatible STEP & CSV export",
                 font=FONT_SM, bg=BG3, fg=TEXT_DIM).pack(side="left", padx=4)

        # ── Main content area ──
        content = tk.Frame(self, bg=BG)
        content.pack(fill="both", expand=True, padx=0, pady=0)

        # Left panel — controls
        left = tk.Frame(content, bg=BG2, width=240)
        left.pack(side="left", fill="y", padx=0, pady=0)
        left.pack_propagate(False)
        self._build_controls(left)

        # Centre — plot
        centre = tk.Frame(content, bg=BG)
        centre.pack(side="left", fill="both", expand=True)
        self._build_plot(centre)

        # Right panel — properties
        self._props_panel = PropertiesPanel(content, width=230)
        self._props_panel.pack(side="right", fill="y")
        self._props_panel.pack_propagate(False)

        # ── Status bar ──
        self._status_var = tk.StringVar(value="Ready.")
        status = tk.Label(self, textvariable=self._status_var,
                          font=FONT_SM, bg=BG3, fg=TEXT_DIM,
                          anchor="w", padx=10, pady=4)
        status.pack(fill="x", side="bottom")

    def _build_controls(self, parent):
        pad = dict(padx=16, pady=5)

        tk.Label(parent, text="Parameters", font=FONT_HEAD,
                 bg=BG2, fg=ACCENT).pack(anchor="w", **pad)

        # NACA code
        tk.Label(parent, text="NACA Code", font=FONT_SM,
                 bg=BG2, fg=TEXT_DIM).pack(anchor="w", padx=16)
        self._code_var = tk.StringVar(value="2412")
        entry = tk.Entry(parent, textvariable=self._code_var,
                         font=("Courier", 13, "bold"), width=10,
                         bg=BG3, fg=ACCENT, insertbackground=ACCENT,
                         relief="flat", bd=6)
        entry.pack(anchor="w", padx=16, pady=(2, 6))
        ToolTip(entry, "4-digit (e.g. 2412) or 5-digit (e.g. 23012)")

        # Chord length
        tk.Label(parent, text="Chord Length (mm)", font=FONT_SM,
                 bg=BG2, fg=TEXT_DIM).pack(anchor="w", padx=16)
        self._chord_var = tk.DoubleVar(value=200.0)
        chord_spin = tk.Spinbox(parent, from_=10, to=10000, increment=10,
                                textvariable=self._chord_var,
                                font=FONT_BODY, width=10,
                                bg=BG3, fg=TEXT, buttonbackground=BG3,
                                relief="flat", bd=4)
        chord_spin.pack(anchor="w", padx=16, pady=(2, 6))

        # Number of points
        tk.Label(parent, text="Points per Surface", font=FONT_SM,
                 bg=BG2, fg=TEXT_DIM).pack(anchor="w", padx=16)
        self._npts_var = tk.IntVar(value=100)
        npts_spin = tk.Spinbox(parent, from_=20, to=500, increment=10,
                               textvariable=self._npts_var,
                               font=FONT_BODY, width=10,
                               bg=BG3, fg=TEXT, buttonbackground=BG3,
                               relief="flat", bd=4)
        npts_spin.pack(anchor="w", padx=16, pady=(2, 16))
        ToolTip(npts_spin, "More points = smoother curve (50–200 recommended)")

        # Generate button
        StyledButton(parent, text="⟳  Generate", command=self._generate,
                     color=ACCENT).pack(fill="x", padx=16, pady=(0, 6))

        ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=16, pady=10)

        tk.Label(parent, text="Export", font=FONT_HEAD,
                 bg=BG2, fg=ACCENT2).pack(anchor="w", padx=16)

        StyledButton(parent, text="💾  Export CSV", command=self._export_csv,
                     color="#4db6ac").pack(fill="x", padx=16, pady=(6, 4))
        StyledButton(parent, text="📐  Export STEP", command=self._export_step,
                     color="#7986cb").pack(fill="x", padx=16, pady=(0, 6))

        ToolTip(parent, "")   # spacer

    def _build_plot(self, parent):
        self._fig = build_figure()
        canvas = FigureCanvasTkAgg(self._fig, master=parent)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=8)
        self._canvas = canvas

    # ── Logic ────────────────────────────────────────────────────────────────

    def _set_status(self, msg, color=TEXT_DIM):
        self._status_var.set(msg)
        # find the label widget (last child)
        for w in self.winfo_children():
            if isinstance(w, tk.Label) and w.cget("textvariable") == str(self._status_var):
                w.config(fg=color)

    def _generate(self):
        code  = self._code_var.get().strip()
        chord = self._chord_var.get()
        npts  = self._npts_var.get()

        try:
            xu, yu, xl, yl, info = generate_airfoil(code, npts, chord)
            props = get_properties(xu, yu, xl, yl, chord)
        except Exception as exc:
            messagebox.showerror("Generation Error", str(exc))
            self._set_status(f"Error: {exc}", ERR)
            return

        self._xu, self._yu = xu, yu
        self._xl, self._yl = xl, yl
        self._info  = info
        self._props = props

        plot_airfoil(self._fig, xu, yu, xl, yl, info, props)
        self._canvas.draw()
        self._props_panel.update(props)
        self._set_status(
            f"Generated NACA {code}  |  chord {chord:.1f} mm  |  "
            f"t/c {props['max_thickness_pct_chord']:.1f}%  |  "
            f"camber {props['max_camber_pct_chord']:.2f}%",
            SUCCESS,
        )

    def _require_airfoil(self) -> bool:
        if self._xu is None:
            messagebox.showwarning("No Airfoil", "Generate an airfoil first.")
            return False
        return True

    def _export_csv(self):
        if not self._require_airfoil():
            return
        code = self._info["code"]
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"NACA_{code}.csv",
            title="Save CSV",
        )
        if not path:
            return
        try:
            out = export_csv(self._xu, self._yu, self._xl, self._yl, path, self._info)
            self._set_status(f"CSV saved → {out}", SUCCESS)
        except Exception as exc:
            messagebox.showerror("Export Error", str(exc))

    def _export_step(self):
        if not self._require_airfoil():
            return
        code = self._info["code"]
        path = filedialog.asksaveasfilename(
            defaultextension=".step",
            filetypes=[("STEP files", "*.step"), ("STP files", "*.stp")],
            initialfile=f"NACA_{code}.step",
            title="Save STEP",
        )
        if not path:
            return
        self._set_status("Exporting STEP… (this may take a few seconds)", TEXT_DIM)
        self.update_idletasks()

        def _do_export():
            try:
                out = export_step(self._xu, self._yu, self._xl, self._yl, path, self._info)
                self.after(0, lambda: self._set_status(f"STEP saved → {out}", SUCCESS))
            except Exception as exc:
                self.after(0, lambda: messagebox.showerror("Export Error", str(exc)))

        threading.Thread(target=_do_export, daemon=True).start()
