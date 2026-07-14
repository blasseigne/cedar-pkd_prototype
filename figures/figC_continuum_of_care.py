"""
figures/figC_continuum_of_care.py
Figure C — CEDAR-PKD, BIRCH-PKD, and ASPEN-PKD: Continuum of Care

Addresses DOD PRMRP Scientist Reviewer B concern:
  'CEDAR-PKD ... does not seem to be too exciting and necessary ...
   BIRCH should be able to provide concise and relevant explanations/answers
   on as needed bases.'

Shows that CEDAR, BIRCH, and ASPEN activate at DIFFERENT points in the ADPKD
patient journey and address DIFFERENT cognitive needs — complementary, not redundant.

Generation
----------
    python3 figures/figC_continuum_of_care.py
"""

import os
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from figures.style import apply_cedar_style, save_figure

# ── Colours ───────────────────────────────────────────────────────────────────
CEDAR_C  = "#2471A3"
BIRCH_C  = "#1E8449"
ASPEN_C  = "#7D3C98"
CEDAR_LT = "#D6EAF8"
BIRCH_LT = "#D5F5E3"
ASPEN_LT = "#E8DAEF"
CEDAR_MD = "#AED6F1"
BIRCH_MD = "#A9DFBF"
ASPEN_MD = "#D2B4DE"
DARK     = "#2C3E50"
GRAY     = "#566573"
LGRAY    = "#EAECEE"
WHITE    = "#FFFFFF"

# ── Figure dimensions ─────────────────────────────────────────────────────────
FW = 7.0

# ── Vertical layout: computed BOTTOM-UP so figure height matches content ──────
# All values in data units (= inches, since xlim/ylim match figure size)
CARD_BOT  = 0.30
CARD_PAD  = 0.10   # padding below quote box

QUOT_H    = 0.44   # example-question box height
QUOT_GAP  = 0.14   # gap: bullet bottom → quote top

BULL_DY   = 0.093  # vertical step per bullet
N_BULLS   = 7
BULL_GAP  = 0.12   # gap: mode bottom → bullet top

MODE_H    = 0.26
MODE_GAP  = 0.06   # gap: header bottom → mode top

HDR_H     = 0.48

# --- derived positions (bottom-up) ---
_quot_bot  = CARD_BOT + CARD_PAD          # 0.40
_quot_top  = _quot_bot + QUOT_H           # 0.84
_bull_bot  = _quot_top + QUOT_GAP         # 0.98
_bull_top  = _bull_bot + N_BULLS * BULL_DY  # 1.631
_mode_bot  = _bull_top + BULL_GAP         # 1.751
_hdr_bot   = _mode_bot + MODE_GAP + MODE_H  # 2.037
CARD_TOP   = _hdr_bot + HDR_H             # 2.517
CARD_H     = CARD_TOP - CARD_BOT          # 2.217

BNR_H      = 0.65
BNR_BOT    = CARD_TOP + 0.09             # 2.607
BNR_TOP    = BNR_BOT + BNR_H            # 3.257
TL_Y       = BNR_BOT + BNR_H * 0.56     # ≈ 2.971

FH = BNR_TOP + 0.23                      # ≈ 3.49

# ── Column positions ──────────────────────────────────────────────────────────
C1_X, C1_W = 0.13, 1.90   # CEDAR-PKD
C2_X, C2_W = 2.37, 2.06   # BIRCH-PKD
C3_X, C3_W = 4.57, 2.30   # ASPEN-PKD


# ── Primitives ────────────────────────────────────────────────────────────────

def _rbox(ax, x, y, w, h, fc, ec, lw=0.9, r=0.07):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad={r}",
        facecolor=fc, edgecolor=ec, linewidth=lw,
        clip_on=False,
    ))


def _t(ax, x, y, s, **kw):
    ax.text(x, y, s, **kw)


# ── Card builder ──────────────────────────────────────────────────────────────

def _card(ax, cx, cw, name, sub, mode, bullets, quote,
          hdr_c, lt_c, md_c):

    # Panel background
    _rbox(ax, cx, CARD_BOT, cw, CARD_H, fc=lt_c, ec=hdr_c, lw=1.3, r=0.09)

    # Header bar
    _rbox(ax, cx, _hdr_bot, cw, HDR_H, fc=hdr_c, ec=hdr_c, lw=0, r=0.08)
    _t(ax, cx + cw/2, _hdr_bot + HDR_H * 0.64, name,
       ha="center", va="center", fontsize=9.5, color=WHITE, fontweight="bold")
    _t(ax, cx + cw/2, _hdr_bot + HDR_H * 0.22, sub,
       ha="center", va="center", fontsize=6.0, color=WHITE,
       fontstyle="italic", alpha=0.90)

    # Mode strip
    inset = 0.09
    _rbox(ax, cx + inset, _mode_bot, cw - 2*inset, MODE_H,
          fc=md_c, ec=hdr_c, lw=0.6, r=0.05)
    _t(ax, cx + cw/2, _mode_bot + MODE_H/2, mode,
       ha="center", va="center", fontsize=6.6, color=hdr_c, fontweight="bold")

    # Bullet list
    x0 = cx + 0.13
    for i, item in enumerate(bullets):
        _t(ax, x0, _bull_top - i * BULL_DY, f"• {item}",
           ha="left", va="top", fontsize=6.3, color=DARK)

    # Example question box
    _rbox(ax, cx + inset, _quot_bot, cw - 2*inset, QUOT_H,
          fc=WHITE, ec=hdr_c, lw=0.9, r=0.05)
    _t(ax, cx + cw/2, _quot_bot + QUOT_H/2, quote,
       ha="center", va="center", fontsize=6.2,
       color=hdr_c, fontstyle="italic", multialignment="center",
       linespacing=1.35)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    apply_cedar_style()

    fig, ax = plt.subplots(figsize=(FW, FH))
    ax.set_xlim(0, FW)
    ax.set_ylim(0, FH)
    ax.axis("off")
    fig.patch.set_facecolor(WHITE)

    # ── Journey banner ────────────────────────────────────────────────────────
    _rbox(ax, 0.11, BNR_BOT, FW - 0.22, BNR_H,
          fc=LGRAY, ec="#BDC3C7", lw=0.7, r=0.07)

    # Timeline arrow
    ax.annotate("",
                xy=(6.76, TL_Y), xytext=(0.25, TL_Y),
                arrowprops=dict(arrowstyle="-|>", color=DARK, lw=1.8,
                                mutation_scale=10))
    _t(ax, 6.88, TL_Y, "Time",
       ha="left", va="center", fontsize=7.5, color=DARK, fontweight="bold")

    # Phase dividers
    for dx in [2.35, 4.60]:
        ax.plot([dx, dx], [TL_Y - 0.09, TL_Y + 0.09],
                color="#BDC3C7", lw=1.0)

    # Phase labels
    for px0, px1, label, col in [
        (0.25, 2.35, "Pre-diagnosis &\nEarly Disease",            CEDAR_C),
        (2.37, 4.60, "Ongoing Management\n& Clinical Decisions",  BIRCH_C),
        (4.62, 6.76, "Advanced Care &\nGenetic Testing",          ASPEN_C),
    ]:
        _t(ax, (px0 + px1)/2, TL_Y + 0.09, label,
           ha="center", va="bottom", fontsize=5.8,
           color=col, fontweight="bold", multialignment="center",
           linespacing=1.2)

    # Milestone dots
    milestones = [
        (0.75, "Symptoms"),
        (1.52, "Diagnosis"),
        (2.88, "Nephrology"),
        (3.80, "CKD progr."),
        (5.00, "Genetic\ntesting"),
        (5.92, "CKD Stg 4-5"),
    ]
    for mx, ml in milestones:
        ax.plot(mx, TL_Y, "o", ms=4.5, color=DARK, zorder=3)
        _t(ax, mx, TL_Y - 0.05, ml,
           ha="center", va="top", fontsize=5.0, color=GRAY,
           multialignment="center", linespacing=1.2)

    # Dashed connectors: card tops → banner
    for cx, cw, col in [(C1_X, C1_W, CEDAR_C),
                         (C2_X, C2_W, BIRCH_C),
                         (C3_X, C3_W, ASPEN_C)]:
        ax.plot([cx + cw/2, cx + cw/2], [CARD_TOP, BNR_BOT],
                color=col, lw=0.8, linestyle=":", alpha=0.5)

    # ── Tool cards ────────────────────────────────────────────────────────────
    _card(ax, C1_X, C1_W,
          name="CEDAR-PKD",
          sub="Adaptive Learning Engine",
          mode="Proactive  ·  Unknown unknowns",
          bullets=[
              "Fills gaps patients can't anticipate",
              "Adaptive IRT + BKT item sequencing",
              "Sex, CKD stage & family-planning aware",
              "Role-filtered: patient vs. clinician",
              "Per-topic mastery tracking (BKT)",
              "Flags gaps to BIRCH when P(m)<0.50",
              "Updates BIRCH with mastery state",
          ],
          quote='"What should I even be\nlearning about my diagnosis?"',
          hdr_c=CEDAR_C, lt_c=CEDAR_LT, md_c=CEDAR_MD)

    _card(ax, C2_X, C2_W,
          name="BIRCH-PKD",
          sub="LLM Decision Support",
          mode="Reactive  ·  Known unknowns",
          bullets=[
              "Answers specific questions on demand",
              "RAG over ADPKD literature + KDIGO",
              "Hallucination-resistant LLM design",
              "Triggered by CEDAR mastery gaps",
              "Patient- and clinician-facing modes",
              "Flags genetic questions to ASPEN",
              "Receives mastery updates from CEDAR",
          ],
          quote='"Should I start tolvaptan?\nWhat are the eligibility criteria?"',
          hdr_c=BIRCH_C, lt_c=BIRCH_LT, md_c=BIRCH_MD)

    _card(ax, C3_X, C3_W,
          name="ASPEN-PKD",
          sub="Variant Pathogenicity Scoring",
          mode="Interpretive  ·  Genetic results",
          bullets=[
              "Scores PKD1/PKD2 variants (ABC)",
              "Functional grade + clinical relevance",
              "Outputs standardized clinical comment",
              "ML model + ACMG/ESHG guidelines",
              "Activates when genetic testing ordered",
              "Feeds results back to BIRCH & CEDAR",
              "Reduces variant classification burden",
          ],
          quote='"Is PKD1 c.1234G>A\npathogenic for my patient?"',
          hdr_c=ASPEN_C, lt_c=ASPEN_LT, md_c=ASPEN_MD)

    # ── Figure title ──────────────────────────────────────────────────────────
    fig.suptitle(
        "Figure C  —  CEDAR-PKD, BIRCH-PKD & ASPEN-PKD: "
        "Complementary Tools Across the ADPKD Care Continuum\n"
        "Each tool activates at a different stage of the patient journey "
        "and addresses a distinct cognitive need",
        fontsize=8.5, fontweight="bold", y=1.03,
    )

    plt.tight_layout(pad=0.15)
    save_figure(fig, "figC_continuum_of_care")
    plt.close(fig)
    print("Figure C complete.")


if __name__ == "__main__":
    main()
