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

# ── Colours (matched to proposal overview: Aim 1=ASPEN green, Aim 2=BIRCH brown, Aim 3=CEDAR navy) ──
CEDAR_C  = "#1A2C46"   # dark navy  (Aim 3)
BIRCH_C  = "#7B5B2A"   # warm brown (Aim 2)
ASPEN_C  = "#4E7D4E"   # forest green (Aim 1)
CEDAR_LT = "#C8D6E8"   # light navy
BIRCH_LT = "#EDE0CC"   # light tan
ASPEN_LT = "#D5E8D5"   # light green
CEDAR_MD = "#8AAAC8"   # medium navy
BIRCH_MD = "#CBB898"   # medium tan
ASPEN_MD = "#AACAAA"   # medium green
DARK     = "#2C3E50"
GRAY     = "#566573"
LGRAY    = "#EAECEE"
WHITE    = "#FFFFFF"

# ── Figure dimensions ─────────────────────────────────────────────────────────
FW = 7.0

# ── Vertical layout: computed BOTTOM-UP so figure height matches content ──────
# All values in data units (= inches, since xlim/ylim match figure size)
CARD_BOT  = 0.30
CARD_PAD  = 0.06   # padding below quote box

QUOT_H    = 0.27   # example-question box height
QUOT_GAP  = 0.08   # gap: bullet bottom → quote top

BULL_DY   = 0.093  # vertical step per bullet
N_BULLS   = 6
BULL_GAP  = 0.09   # gap: mode bottom → bullet top

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

BNR_H      = 0.95
BNR_BOT    = CARD_TOP + 0.09
BNR_TOP    = BNR_BOT + BNR_H
TL_Y       = BNR_BOT + BNR_H * 0.67

FH = BNR_TOP + 0.23                      # ≈ 3.49

# ── Column positions — equal widths, equal gaps ───────────────────────────────
C1_X, C1_W = 0.13, 2.00   # CEDAR-PKD
C2_X, C2_W = 2.50, 2.00   # BIRCH-PKD
C3_X, C3_W = 4.87, 2.00   # ASPEN-PKD


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
          hdr_c, lt_c, md_c, aim=None):

    # Panel background
    _rbox(ax, cx, CARD_BOT, cw, CARD_H, fc=lt_c, ec=hdr_c, lw=1.3, r=0.09)

    # Header bar
    _rbox(ax, cx, _hdr_bot, cw, HDR_H, fc=hdr_c, ec=hdr_c, lw=0, r=0.08)
    if aim:
        _t(ax, cx + cw/2, _hdr_bot + HDR_H * 0.87, aim,
           ha="center", va="center", fontsize=6.5, color=WHITE,
           fontweight="bold", alpha=0.85)
    name_y = _hdr_bot + HDR_H * (0.56 if aim else 0.64)
    _t(ax, cx + cw/2, name_y, name,
       ha="center", va="center", fontsize=9.5, color=WHITE, fontweight="bold")
    _t(ax, cx + cw/2, _hdr_bot + HDR_H * 0.18, sub,
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
       color=hdr_c, fontstyle="italic", fontweight="bold",
       multialignment="center", linespacing=1.35)


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

    # Banner header
    _t(ax, FW / 2, BNR_BOT + BNR_H * 0.91,
       "Empowering the ADPKD Community with AI-Driven Tools for Genetic, Clinical, and Educational Advancement",
       ha="center", va="center", fontsize=8.5, color=DARK, fontweight="bold")

    # Timeline arrow
    ax.annotate("",
                xy=(6.55, TL_Y), xytext=(0.25, TL_Y),
                arrowprops=dict(arrowstyle="-|>", color=DARK, lw=1.8,
                                mutation_scale=10))
    _t(ax, 6.59, TL_Y, "Time",
       ha="left", va="center", fontsize=7.5, color=DARK, fontweight="bold")

    # Milestone dots
    milestones = [
        (0.75, "First\nsymptoms"),
        (1.85, "ADPKD\ndiagnosis"),
        (3.20, "Treatment\ninitiation"),
        (4.75, "CKD\nStage 3–4"),
        (5.90, "Transplant\n/ ESRD"),
    ]
    for mx, ml in milestones:
        ax.plot(mx, TL_Y, "o", ms=4.5, color=DARK, zorder=3)
        _t(ax, mx, TL_Y - 0.05, ml,
           ha="center", va="top", fontsize=5.0, color=GRAY,
           multialignment="center", linespacing=1.2)

    # Activation span bars — primary use window per tool
    SPAN_H = 0.062
    sy_aspen = BNR_BOT + 0.235   # top
    sy_birch = BNR_BOT + 0.148   # middle
    sy_cedar = BNR_BOT + 0.061   # bottom

    _t(ax, 0.25, BNR_BOT + 0.300, "Tool use window →",
       ha="left", va="bottom", fontsize=5.0, color=GRAY)

    # ASPEN: from ADPKD diagnosis onward (dx, prognosis, therapy, family planning, donor eval)
    _rbox(ax, 1.85, sy_aspen, 4.70, SPAN_H, fc=ASPEN_LT, ec=ASPEN_C, lw=0.9, r=0.025)
    _t(ax, 1.85 + 2.35, sy_aspen + SPAN_H / 2, "ASPEN-PKD (Aim 1)",
       ha="center", va="center", fontsize=5.4, color=ASPEN_C, fontweight="bold")

    # BIRCH: full timeline
    _rbox(ax, 0.25, sy_birch, 6.30, SPAN_H, fc=BIRCH_LT, ec=BIRCH_C, lw=0.9, r=0.025)
    _t(ax, 0.25 + 3.15, sy_birch + SPAN_H / 2, "BIRCH-PKD (Aim 2)",
       ha="center", va="center", fontsize=5.4, color=BIRCH_C, fontweight="bold")

    # CEDAR: full timeline
    _rbox(ax, 0.25, sy_cedar, 6.30, SPAN_H, fc=CEDAR_LT, ec=CEDAR_C, lw=0.9, r=0.025)
    _t(ax, 0.25 + 3.15, sy_cedar + SPAN_H / 2, "CEDAR-PKD (Aim 3)",
       ha="center", va="center", fontsize=5.4, color=CEDAR_C, fontweight="bold")

    # Dashed connectors: card tops → banner
    for cx, cw, col in [(C1_X, C1_W, ASPEN_C),
                         (C2_X, C2_W, BIRCH_C),
                         (C3_X, C3_W, CEDAR_C)]:
        ax.plot([cx + cw/2, cx + cw/2], [CARD_TOP, BNR_BOT],
                color=col, lw=0.8, linestyle=":", alpha=0.5)

    # ── Tool cards ────────────────────────────────────────────────────────────
    _card(ax, C1_X, C1_W,
          name="ASPEN-PKD",
          sub="Variant Pathogenicity Scoring",
          mode="Interpretive  ·  Genetic results",
          bullets=[
              "Scores major/minor KDIGO gene variants",
              "Functional grade + clinical relevance",
              "Outputs standardized clinical comment",
              "ML model + ACMG/ESHG guidelines",
              "Reduces variant classification burden",
              "Patient/care partner-facing views",
          ],
          quote='"Is PKD1 c.1234G>A\npathogenic for my patient?"',
          hdr_c=ASPEN_C, lt_c=ASPEN_LT, md_c=ASPEN_MD,
          aim="Aim 1")

    _card(ax, C2_X, C2_W,
          name="BIRCH-PKD",
          sub="LLM Decision Support",
          mode="Reactive  ·  Known unknowns",
          bullets=[
              "Answers specific questions on demand",
              "RAG over ADPKD literature + KDIGO",
              "Hallucination-resistant LLM design",
              "Patient/care partner-facing modes",
              "Source-cited responses for auditability",
              "Covers tolvaptan, genetics, diet, progr., etc.",
          ],
          quote='"Should I start tolvaptan?\nWhat are the eligibility criteria?"',
          hdr_c=BIRCH_C, lt_c=BIRCH_LT, md_c=BIRCH_MD,
          aim="Aim 2")

    _card(ax, C3_X, C3_W,
          name="CEDAR-PKD",
          sub="Adaptive Learning Engine",
          mode="Proactive  ·  Unknown unknowns",
          bullets=[
              "Fills gaps patients cannot anticipate",
              "Adaptive IRT + BKT item sequencing",
              "Sex, stage & family-planning aware",
              "Patient/care partner & clinician roles",
              "Per-topic mastery tracking (BKT)",
              "Misconception-targeted feedback on errors",
          ],
          quote='"What should I even be\nlearning about my diagnosis?"',
          hdr_c=CEDAR_C, lt_c=CEDAR_LT, md_c=CEDAR_MD,
          aim="Aim 3")

    plt.tight_layout(pad=0.15)
    save_figure(fig, "figC_continuum_of_care")
    plt.close(fig)
    print("Figure C complete.")


if __name__ == "__main__":
    main()
