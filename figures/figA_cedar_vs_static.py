"""
figures/figA_cedar_vs_static.py
Figure A — CEDAR-PKD vs. Generic Online Resources

Addresses DOD PRMRP Scientist Reviewer B concern (Research Strategy & Impact):
  'CEDAR-PKD ... does not seem to be too exciting and necessary, considering
   the availability of various educational resources online.'

Three-column layout: (1) Generic static resource → same questions for everyone;
(2) CEDAR patient path → sex/stage/family-planning prioritised items;
(3) CEDAR clinician path → role-filtered, high-discrimination items.
Same 20-item bank; entirely different personalised sequences.

Generation
----------
    python figures/figA_cedar_vs_static.py
"""

import os
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from figures.style import apply_cedar_style, save_figure

# ── Colour palette ────────────────────────────────────────────────────────────
CEDAR_BLUE   = "#2980B9"
CEDAR_DARK   = "#2C3E50"
STATIC_HDR   = "#717D7E"
STATIC_BG    = "#EAECEE"
STATIC_Q_FC  = "#D5D8DC"
STATIC_Q_EC  = "#A6ACAF"
PATIENT_C    = "#C0392B"    # rose-red (patient path)
PHYSICIAN_C  = "#1A7D5A"    # dark teal (physician path)
BADGE_SEX    = "#C0392B"
BADGE_FP     = "#7D3C98"
BADGE_STAGE  = "#CA6F1E"
BADGE_ROLE   = "#1A5276"
CEDAR_LT_P   = "#FDEDEC"   # patient panel background
CEDAR_LT_PH  = "#E9F7EF"   # physician panel background
CEDAR_HDR_P  = "#C0392B"
CEDAR_HDR_PH = "#1A7D5A"
WHITE        = "#FFFFFF"
GRAY_MED     = "#AAB7B8"
GRAY_DARK    = "#566573"

# ── Layout constants (all in data units; figure is 7.0 × 5.2 inches) ─────────
FW, FH = 7.0, 5.2

# Column x positions and widths
C1_X, C1_W = 0.15, 1.96   # Static resource
C2_X, C2_W = 2.27, 2.15   # CEDAR: Patient
C3_X, C3_W = 4.58, 2.25   # CEDAR: Physician

P_BOT = 0.45   # panel bottom (data y)
P_TOP = 4.95   # panel top

HDR_H   = 0.56   # column header height
Q_H     = 0.40   # question box height
BDG_H   = 0.17   # badge strip height
BDG_G   = 0.05   # gap: bottom of q-box → top of badge strip
ROW_G   = 0.14   # gap: bottom of badge strip → top of next q-box

# Height per question entry (box + badge + gaps)
SLOT_H  = Q_H + BDG_G + BDG_H + ROW_G   # = 0.76

# Y of top of first question box, just below the header
Q_TOP   = P_TOP - HDR_H - 0.18   # = 4.21


# ── Primitives ────────────────────────────────────────────────────────────────

def _rbox(ax, x, y, w, h, fc, ec, lw=0.9, r=0.08):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad={r}",
        facecolor=fc, edgecolor=ec, linewidth=lw,
    ))


def _t(ax, x, y, s, **kw):
    ax.text(x, y, s, **kw)


def _arr(ax, x, y0, y1, color, lw=0.9):
    """Downward arrow from y0 to y1 at column x-centre."""
    ax.annotate("",
                xy=(x, y1), xytext=(x, y0),
                arrowprops=dict(arrowstyle="-|>", color=color,
                                lw=lw, mutation_scale=6))


def _col_header(ax, cx, cy, cw, ch, title, sub, hdr_fc, sub_c=WHITE):
    """Draw a rounded column header box."""
    _rbox(ax, cx, cy, cw, ch, fc=hdr_fc, ec=hdr_fc, lw=0, r=0.08)
    _t(ax, cx + cw / 2, cy + ch * 0.62, title,
       ha="center", va="center", fontsize=8.5, color=WHITE, fontweight="bold")
    _t(ax, cx + cw / 2, cy + ch * 0.24, sub,
       ha="center", va="center", fontsize=6.0, color=sub_c, fontstyle="italic")


def _q_box(ax, cx, cy_top, cw, label, fc, ec, inset=0.08):
    """Draw a question box whose TOP edge is at cy_top."""
    x  = cx + inset
    y  = cy_top - Q_H          # bottom-left y in data coords
    w  = cw - 2 * inset
    _rbox(ax, x, y, w, Q_H, fc=fc, ec=ec, lw=0.9, r=0.07)
    _t(ax, x + w / 2, y + Q_H / 2, label,
       ha="center", va="center", fontsize=6.2, color=CEDAR_DARK, wrap=False)
    return y   # return box bottom y


def _badges(ax, cx, box_bottom, cw, badges, inset=0.08):
    """
    Draw badge strip below box_bottom.
    badges : list of (label_str, color)
    Returns y of bottom of badge strip.
    """
    strip_top = box_bottom - BDG_G
    strip_bot = strip_top - BDG_H
    bx  = cx + inset
    avail_w = cw - 2 * inset
    # Distribute badges equally
    n  = len(badges)
    bw = (avail_w - (n - 1) * 0.06) / n
    for i, (lbl, fc) in enumerate(badges):
        bxi = bx + i * (bw + 0.06)
        _rbox(ax, bxi, strip_bot, bw, BDG_H, fc=fc, ec=fc, lw=0, r=0.04)
        _t(ax, bxi + bw / 2, strip_bot + BDG_H / 2, lbl,
           ha="center", va="center", fontsize=5.0, color=WHITE, fontweight="bold")
    return strip_bot   # bottom y of badge strip


def _column(ax, cx, cw, questions, fc, ec, hdr_fc, panel_fc,
            hdr_title, hdr_sub, show_badges=True):
    """
    Draw a full column: background + header + question stack.
    questions : list of (label, [(badge_text, badge_color), ...])
    Returns the y of the last element drawn.
    """
    # Panel background
    _rbox(ax, cx, P_BOT, cw, P_TOP - P_BOT, fc=panel_fc, ec=ec, lw=1.0, r=0.10)

    # Column header
    _col_header(ax, cx, P_TOP - HDR_H, cw, HDR_H, hdr_title, hdr_sub, hdr_fc)

    # Questions — stacked top-down
    cur_top = Q_TOP
    for i, (label, badges) in enumerate(questions):
        box_bot = _q_box(ax, cx, cur_top, cw, label, fc=fc, ec=ec)
        if show_badges and badges:
            badge_bot = _badges(ax, cx, box_bot, cw, badges)
            next_top  = badge_bot - ROW_G
        else:
            next_top  = box_bot - BDG_G - BDG_H - ROW_G   # same space even with no badges
        if i < len(questions) - 1:
            _arr(ax, cx + cw / 2, next_top + ROW_G / 2, next_top + 0.03, ec)
        cur_top = next_top

    return cur_top


# ── Content definitions ───────────────────────────────────────────────────────

STATIC_QS = [
    ("What is ADPKD and how common is it?",      []),
    ("Which genes cause ADPKD (PKD1, PKD2)?",    []),
    ("What are the symptoms of ADPKD?",          []),
    ("How is ADPKD diagnosed?",                  []),
]

PATIENT_QS = [
    ("ADPKD complications in women:\naneurysm & liver cyst risk",
     [("+Sex-specific", BADGE_SEX)]),
    ("Family planning & IVF/PGT\noptions with ADPKD",
     [("+Sex-specific", BADGE_SEX), ("+Family planning", BADGE_FP)]),
    ("Genetic testing value for\nreproductive decisions",
     [("+Family planning", BADGE_FP)]),
    ("PKD2 prognosis at your\nCKD Stage 2",
     [("+CKD stage match", BADGE_STAGE)]),
]

PHYSICIAN_QS = [
    ("PKD1 vs. PKD2: severity,\nprognosis & management",
     [("+Physician only", BADGE_ROLE)]),
    ("Tolvaptan eligibility criteria\nby CKD stage",
     [("+Physician only", BADGE_ROLE), ("+CKD stage match", BADGE_STAGE)]),
    ("Counselling patients on\npreimplantation genetic testing",
     [("+Sex-specific", BADGE_SEX), ("+Family planning", BADGE_FP)]),
    ("Barriers to genetic testing\nin nephrology practice",
     [("+Physician only", BADGE_ROLE)]),
]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    apply_cedar_style()

    fig, ax = plt.subplots(figsize=(FW, FH))
    ax.set_xlim(0, FW)
    ax.set_ylim(0, FH)
    ax.axis("off")
    fig.patch.set_facecolor(WHITE)

    # ── Column 1 — Static resource ────────────────────────────────────────────
    _column(ax, C1_X, C1_W, STATIC_QS,
            fc=STATIC_Q_FC, ec=STATIC_Q_EC,
            hdr_fc=STATIC_HDR, panel_fc=STATIC_BG,
            hdr_title="Generic Online Resource",
            hdr_sub="Same content for every learner",
            show_badges=False)

    # "Any learner" label
    _t(ax, C1_X + C1_W / 2, Q_TOP + 0.07,
       "Any learner", ha="center", va="bottom",
       fontsize=7.0, color=STATIC_HDR, fontweight="bold")

    # Footer note
    _t(ax, C1_X + C1_W / 2, P_BOT + 0.12,
       "[!] No role-filter · No demographic tailoring",
       ha="center", va="center", fontsize=5.5, color=STATIC_HDR, fontstyle="italic")

    # ── VS. separator ─────────────────────────────────────────────────────────
    vx = C1_X + C1_W + (C2_X - C1_X - C1_W) / 2
    ax.plot([vx, vx], [P_BOT + 0.3, P_TOP - 0.3],
            color=GRAY_MED, lw=0.8, linestyle="--")
    _t(ax, vx, (P_BOT + P_TOP) / 2, "VS.",
       ha="center", va="center", fontsize=11.5,
       color=GRAY_DARK, fontweight="bold",
       bbox=dict(facecolor=WHITE, edgecolor=GRAY_MED,
                 boxstyle="round,pad=0.18", linewidth=0.8))

    # ── Column 2 — CEDAR patient path ────────────────────────────────────────
    _column(ax, C2_X, C2_W, PATIENT_QS,
            fc=WHITE, ec=PATIENT_C,
            hdr_fc=PATIENT_C, panel_fc=CEDAR_LT_P,
            hdr_title="CEDAR-PKD: Patient",
            hdr_sub="Female · CKD Stage 2 · Family planning")

    _t(ax, C2_X + C2_W / 2, P_BOT + 0.12,
       "[+] Role-filtered · Sex-tailored · Stage-matched",
       ha="center", va="center", fontsize=5.5, color=PATIENT_C, fontstyle="italic")

    # ── Column 3 — CEDAR physician path ──────────────────────────────────────
    _column(ax, C3_X, C3_W, PHYSICIAN_QS,
            fc=WHITE, ec=PHYSICIAN_C,
            hdr_fc=PHYSICIAN_C, panel_fc=CEDAR_LT_PH,
            hdr_title="CEDAR-PKD: Clinician",
            hdr_sub="Experienced PCP · Role-filtered")

    _t(ax, C3_X + C3_W / 2, P_BOT + 0.12,
       "[+] Role-filtered · High-discrimination items first",
       ha="center", va="center", fontsize=5.5, color=PHYSICIAN_C, fontstyle="italic")

    # ── Shared item bank callout ──────────────────────────────────────────────
    _rbox(ax, C2_X, P_TOP + 0.05, C3_X + C3_W - C2_X, 0.24,
          fc="#D6EAF8", ec=CEDAR_BLUE, lw=0.8, r=0.05)
    _t(ax, (C2_X + C3_X + C3_W) / 2, P_TOP + 0.17,
       "Same 20-item ADPKD question bank  --  entirely different personalised sequence per learner",
       ha="center", va="center", fontsize=6.5, color=CEDAR_DARK)

    # ── Badge legend ──────────────────────────────────────────────────────────
    legend_items = [
        (BADGE_SEX,   "+Sex-specific"),
        (BADGE_FP,    "+Family planning"),
        (BADGE_STAGE, "+CKD stage match"),
        (BADGE_ROLE,  "+Clinician only"),
    ]
    lx, ly = 2.27, 0.18
    _t(ax, lx - 0.05, ly + 0.06, "Boost key:",
       ha="left", va="center", fontsize=6.5, color=CEDAR_DARK, fontweight="bold")
    bx = lx + 0.80
    for fc, label in legend_items:
        _rbox(ax, bx, ly - 0.01, 0.14, 0.14, fc=fc, ec=fc, lw=0, r=0.03)
        _t(ax, bx + 0.18, ly + 0.06, label,
           ha="left", va="center", fontsize=6.0, color=CEDAR_DARK)
        bx += 1.05

    # ── Figure title ──────────────────────────────────────────────────────────
    fig.suptitle(
        "Figure A  —  CEDAR-PKD Adaptive Learning vs. Generic Online Resources\n"
        "Same item bank · Role-filtered · Demographically personalised · Mastery-tracked",
        fontsize=8.5, fontweight="bold", y=1.04,
    )

    plt.tight_layout(pad=0.2)
    save_figure(fig, "figA_cedar_vs_static")
    plt.close(fig)
    print("Figure A complete.")


if __name__ == "__main__":
    main()
