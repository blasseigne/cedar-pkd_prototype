"""
figures/style.py
Shared matplotlib style for all CEDAR-PKD prototype figures.
Import and call apply_cedar_style() at the top of every figure script
to ensure consistent fonts, colors, and DPI across all 8 grant figures.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl

# ---------------------------------------------------------------------------
# Color palette
# One color per user profile, carried consistently through Figures 5, 6, 7.
# Also used for topic areas and audience tags throughout.
# ---------------------------------------------------------------------------

# User / profile colors
PROFILE_COLORS = {
    "newly_diagnosed_patient":      "#4C9BE8",   # sky blue
    "average_ability_patient":      "#4C9BE8",   # sky blue (same as newly diagnosed)
    "experienced_patient":          "#F4845F",   # coral
    "primary_care_physician":       "#56B29A",   # teal
    "nephrologist":                 "#9B72CF",   # purple
}

# Demographic profile colors (Figure 7)
DEMO_COLORS = {
    "female_early_family_planning": "#E85D8A",   # rose
    "male_advanced":                "#3D7EBF",   # steel blue
    "treating_physician":           "#56B29A",   # teal (matches physician above)
}

# Topic area colors (Figures 4, 5, 6, 7)
TOPIC_COLORS = {
    "kidney_basics":    "#AED6F1",   # light blue
    "adpkd_diagnosis":  "#A9DFBF",   # light green
    "adpkd_genetics":   "#F9E79F",   # light yellow
}

# Bloom's taxonomy level colors (Figure 4)
BLOOMS_COLORS = {
    "remember":    "#D6EAF8",   # lightest blue
    "understand":  "#85C1E9",   # medium blue
    "apply":       "#2E86C1",   # dark blue
}

# Neutral grays
GRAY_LIGHT  = "#F2F3F4"
GRAY_MED    = "#AAB7B8"
GRAY_DARK   = "#566573"

# Mastery threshold line color
THRESHOLD_COLOR = "#E74C3C"   # red

# Adaptive vs static
ADAPTIVE_COLOR = "#27AE60"    # green
STATIC_COLOR   = "#E67E22"    # orange

# ---------------------------------------------------------------------------
# Standard figure sizes (inches) — single-column and double-column for grants
# ---------------------------------------------------------------------------
FIG_SINGLE  = (3.5, 3.0)   # single column
FIG_DOUBLE  = (7.0, 3.5)   # double column / wide
FIG_SQUARE  = (3.5, 3.5)   # square single column
FIG_TALL    = (3.5, 5.0)   # tall single column
FIG_PANEL22 = (7.0, 6.0)   # 2x2 panel (Figure 5)
FIG_PANEL13 = (7.0, 3.5)   # 1x3 panel (Figure 7)

# ---------------------------------------------------------------------------
# Grant-quality output settings
# ---------------------------------------------------------------------------
OUTPUT_DPI  = 300
OUTPUT_DIR  = "outputs"


def apply_cedar_style():
    """
    Apply the shared CEDAR-PKD style to matplotlib.
    Call once at the top of each figure script, before any plotting.
    """
    mpl.rcParams.update({
        # Font
        "font.family":          "sans-serif",
        "font.sans-serif":      ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size":            8,
        "axes.titlesize":       9,
        "axes.labelsize":       8,
        "xtick.labelsize":      7,
        "ytick.labelsize":      7,
        "legend.fontsize":      7,

        # Lines and markers
        "lines.linewidth":      1.5,
        "lines.markersize":     5,

        # Axes
        "axes.spines.top":      False,
        "axes.spines.right":    False,
        "axes.grid":            True,
        "grid.alpha":           0.3,
        "grid.linestyle":       "--",
        "grid.linewidth":       0.5,
        "axes.axisbelow":       True,

        # Figure
        "figure.dpi":           150,       # screen preview
        "savefig.dpi":          OUTPUT_DPI,
        "savefig.bbox":         "tight",
        "savefig.facecolor":    "white",

        # Legend
        "legend.framealpha":    0.8,
        "legend.frameon":       True,
        "legend.edgecolor":     GRAY_MED,
    })


def save_figure(fig, filename, output_dir=OUTPUT_DIR):
    """
    Save a figure as both PNG and PDF at grant quality.

    Parameters
    ----------
    fig      : matplotlib Figure
    filename : str, without extension (e.g. 'fig2_icc')
    output_dir : str, directory to save into
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    base = os.path.join(output_dir, filename)
    fig.savefig(f"{base}.png", dpi=OUTPUT_DPI, bbox_inches="tight", facecolor="white")
    fig.savefig(f"{base}.pdf", bbox_inches="tight", facecolor="white")
    print(f"  Saved: {base}.png + {base}.pdf")
