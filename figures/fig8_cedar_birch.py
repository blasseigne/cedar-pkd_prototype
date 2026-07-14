"""
figures/fig8_cedar_birch.py
Figure 8 — CEDAR-PKD vs. BIRCH-PKD: Complementary but Distinct Tools

A schematic diagram differentiating CEDAR-PKD from BIRCH-PKD for the DOD
PRMRP resubmission.  DOD Reviewer B questioned whether CEDAR was necessary
given the existence of BIRCH ("why do you need both?").

The diagram shows that the two tools address different types of knowledge gaps:

    BIRCH-PKD   — Reactive.  Answers the questions a user knows to ask.
                  Fills *known unknowns*.

    CEDAR-PKD   — Proactive. Identifies and fills the gaps a user doesn't
                  know they have.  Fills *unknown unknowns*.

Together they provide comprehensive ADPKD knowledge support that neither
tool could deliver alone.

Generation
----------
    python figures/fig8_cedar_birch.py
"""

import os
import sys

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import matplotlib as mpl
import numpy as np

# ── path setup ────────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from figures.style import apply_cedar_style, save_figure, GRAY_DARK, GRAY_MED, GRAY_LIGHT

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
CEDAR_COLOR   = "#2980B9"   # blue — proactive / structured
BIRCH_COLOR   = "#27AE60"   # green — reactive / responsive
GAP_COLOR     = "#8E44AD"   # purple — knowledge gap (shared motivation)
ARROW_COLOR   = "#555555"
BG_LIGHT      = "#F8F9FA"
OUTCOME_COLOR = "#E67E22"   # orange — shared outcome

CEDAR_LIGHT   = mpl.colors.to_rgba(CEDAR_COLOR, 0.12)
BIRCH_LIGHT   = mpl.colors.to_rgba(BIRCH_COLOR, 0.12)
GAP_LIGHT     = mpl.colors.to_rgba(GAP_COLOR, 0.10)


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def _box(ax, x, y, w, h, fc, ec, lw=1.2, radius=0.03, zorder=3, alpha=1.0):
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad={radius}",
        facecolor=fc, edgecolor=ec,
        linewidth=lw, zorder=zorder, alpha=alpha,
    )
    ax.add_patch(p)
    return p


def _arrow(ax, x0, y0, x1, y1, color=ARROW_COLOR, lw=1.5, style="->"):
    ax.annotate(
        "", xy=(x1, y1), xytext=(x0, y0),
        arrowprops=dict(
            arrowstyle=style,
            color=color,
            lw=lw,
            connectionstyle="arc3,rad=0.0",
        ),
        zorder=5,
    )


def _label(ax, x, y, text, size=8, color="#1A1A2E", weight="normal",
           ha="center", va="center", ls=1.35, zorder=6):
    ax.text(x, y, text, ha=ha, va=va,
            fontsize=size, fontweight=weight,
            color=color, linespacing=ls, zorder=zorder)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    apply_cedar_style()

    fig, ax = plt.subplots(figsize=(7.0, 5.6))
    ax.axis("off")
    ax.set_xlim(0, 7.0)
    ax.set_ylim(0, 5.6)
    fig.patch.set_facecolor("white")

    # ══════════════════════════════════════════════════════════════════════
    # TOP — Shared driver: ADPKD Knowledge Gaps
    # ══════════════════════════════════════════════════════════════════════
    gap_w, gap_h = 3.6, 0.58
    gap_x = (7.0 - gap_w) / 2
    gap_y = 4.55

    _box(ax, gap_x, gap_y, gap_w, gap_h,
         fc=GAP_COLOR, ec=GAP_COLOR, lw=1.8)
    _label(ax, gap_x + gap_w / 2, gap_y + gap_h * 0.64,
           "ADPKD Knowledge Gaps in Patients & Clinicians",
           size=8.5, weight="bold", color="white", ls=1.4)
    _label(ax, gap_x + gap_w / 2, gap_y + gap_h * 0.24,
           "Delayed diagnosis · Genetics literacy · Testing utilisation",
           size=6.8, color="white", ls=1.4)

    # ══════════════════════════════════════════════════════════════════════
    # MIDDLE — Two tool columns
    # ══════════════════════════════════════════════════════════════════════
    col_w   = 2.80
    col_h   = 2.55
    col_y   = 1.55
    birch_x = 0.22
    cedar_x = 7.0 - 0.22 - col_w

    # ── Arrows from gap box down to each tool ────────────────────────────
    _arrow(ax, gap_x + gap_w * 0.28, gap_y,
               birch_x + col_w / 2, col_y + col_h + 0.01,
           color=BIRCH_COLOR, lw=1.5)
    _arrow(ax, gap_x + gap_w * 0.72, gap_y,
               cedar_x + col_w / 2, col_y + col_h + 0.01,
           color=CEDAR_COLOR, lw=1.5)

    # ── BIRCH-PKD column ──────────────────────────────────────────────────
    _box(ax, birch_x, col_y, col_w, col_h,
         fc=BIRCH_LIGHT, ec=BIRCH_COLOR, lw=2.0)

    # Header
    _box(ax, birch_x, col_y + col_h - 0.42, col_w, 0.42,
         fc=BIRCH_COLOR, ec=BIRCH_COLOR, lw=0, radius=0.02)
    _label(ax, birch_x + col_w / 2, col_y + col_h - 0.21,
           "BIRCH-PKD", size=10, weight="bold", color="white")

    # Content rows
    birch_rows = [
        ("Mode",       "Reactive — user-initiated"),
        ("Mechanism",  "Evidence-based Q&A chatbot"),
        ("Gap type",   "Known unknowns"),
        ("Trigger",    "User asks a specific question"),
        ("Output",     "Single focused answer"),
        ("Strength",   "On-demand, any time, any topic"),
    ]
    row_h   = (col_h - 0.42 - 0.08) / len(birch_rows)
    for ri, (label, val) in enumerate(birch_rows):
        ry = col_y + col_h - 0.42 - 0.06 - (ri + 1) * row_h
        _label(ax, birch_x + 0.12, ry + row_h / 2,
               label, size=6.2, weight="bold", color=BIRCH_COLOR, ha="left")
        _label(ax, birch_x + 0.80, ry + row_h / 2,
               val, size=6.2, color="#1A1A2E", ha="left")

    # ── CEDAR-PKD column ─────────────────────────────────────────────────
    _box(ax, cedar_x, col_y, col_w, col_h,
         fc=CEDAR_LIGHT, ec=CEDAR_COLOR, lw=2.0)

    # Header
    _box(ax, cedar_x, col_y + col_h - 0.42, col_w, 0.42,
         fc=CEDAR_COLOR, ec=CEDAR_COLOR, lw=0, radius=0.02)
    _label(ax, cedar_x + col_w / 2, col_y + col_h - 0.21,
           "CEDAR-PKD", size=10, weight="bold", color="white")

    # Content rows
    cedar_rows = [
        ("Mode",       "Proactive — system-initiated"),
        ("Mechanism",  "Adaptive Learning Engine (ALE)"),
        ("Gap type",   "Unknown unknowns"),
        ("Trigger",    "BKT mastery gap detection"),
        ("Output",     "Personalised curriculum path"),
        ("Strength",   "Fills gaps learner didn't know existed"),
    ]
    for ri, (label, val) in enumerate(cedar_rows):
        ry = col_y + col_h - 0.42 - 0.06 - (ri + 1) * row_h
        _label(ax, cedar_x + 0.12, ry + row_h / 2,
               label, size=6.2, weight="bold", color=CEDAR_COLOR, ha="left")
        _label(ax, cedar_x + 0.80, ry + row_h / 2,
               val, size=6.2, color="#1A1A2E", ha="left")

    # ── "vs." divider ────────────────────────────────────────────────────
    mid_x = 7.0 / 2
    ax.plot([mid_x, mid_x], [col_y + 0.15, col_y + col_h - 0.08],
            color=GRAY_MED, lw=0.8, linestyle="--", zorder=2)
    _box(ax, mid_x - 0.22, col_y + col_h / 2 - 0.16, 0.44, 0.32,
         fc="white", ec=GRAY_MED, lw=0.8, radius=0.05)
    _label(ax, mid_x, col_y + col_h / 2,
           "vs.", size=9, weight="bold", color=GRAY_DARK)

    # ══════════════════════════════════════════════════════════════════════
    # BOTTOM — Shared outcome
    # ══════════════════════════════════════════════════════════════════════
    out_w, out_h = 5.20, 0.56
    out_x = (7.0 - out_w) / 2
    out_y = 0.30

    # Arrows down from each tool to outcome box
    _arrow(ax, birch_x + col_w / 2, col_y,
               out_x + out_w * 0.25, out_y + out_h,
           color=BIRCH_COLOR, lw=1.3)
    _arrow(ax, cedar_x + col_w / 2, col_y,
               out_x + out_w * 0.75, out_y + out_h,
           color=CEDAR_COLOR, lw=1.3)

    _box(ax, out_x, out_y, out_w, out_h,
         fc=mpl.colors.to_rgba(OUTCOME_COLOR, 0.10),
         ec=OUTCOME_COLOR, lw=1.8)
    _label(ax, out_x + out_w / 2, out_y + out_h * 0.68,
           "Together: comprehensive ADPKD knowledge support",
           size=7.5, weight="bold", color="#7D3C00")
    _label(ax, out_x + out_w / 2, out_y + out_h * 0.25,
           "Known and unknown gaps addressed — neither tool alone is sufficient",
           size=6.8, color="#7D3C00")

    # ══════════════════════════════════════════════════════════════════════
    # Figure title — placed outside axes via suptitle so it never overlaps
    # ══════════════════════════════════════════════════════════════════════
    fig.suptitle(
        "Figure 8 — CEDAR-PKD vs. BIRCH-PKD: Complementary but Distinct Tools\n"
        "BIRCH fills known unknowns (reactive Q&A); CEDAR fills unknown unknowns "
        "(proactive adaptive curriculum). Neither alone is sufficient.",
        ha="center", fontsize=7.5, fontweight="bold",
        color="#1A1A2E", linespacing=1.4, y=0.99,
    )

    plt.tight_layout(pad=0.3)
    save_figure(fig, "fig8_cedar_birch")
    plt.close(fig)
    print("Figure 8 complete.")


if __name__ == "__main__":
    main()
