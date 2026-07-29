"""
figures/fig1_app_screenshot.py
Figure 1 — CEDAR-PKD Prototype UI: Patient vs. Physician Views

A grant-quality rendering of the CEDAR-PKD Streamlit app showing two
simultaneous views using real question content:

  Left  — Patient view (plain-language, Q4 awaiting answer)
  Right — Physician view (clinical detail, Q6 with correct-answer feedback)

Addresses reviewer concerns: "no ALE proof-of-concept" and "UI too dense
for patients" by demonstrating role-differentiated, accessible design.

Generation
----------
    python figures/fig1_app_screenshot.py
"""

import os
import sys
import textwrap

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import FancyBboxPatch
import numpy as np

# ── path setup ────────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from figures.style import apply_cedar_style, save_figure

# ---------------------------------------------------------------------------
# Color constants
# ---------------------------------------------------------------------------
HEADER_BG     = "#2C3E50"
SIDEBAR_BG    = "#F4F6F7"
PANEL_BG      = "#FFFFFF"
BORDER        = "#D5D8DC"
TEXT_MAIN     = "#1A1A2E"
TEXT_MUTED    = "#566573"

MASTERY_ON    = "#27AE60"   # green  — mastered
MASTERY_OFF   = "#2980B9"   # blue   — in progress
MASTERY_TRACK = "#E5E8E8"   # bar track background

BTN_NORMAL    = "#FDFEFE"
BTN_CORRECT   = "#D5F5E3"
BTN_NEUTRAL   = "#F2F3F4"
EDGE_CORRECT  = "#1E8449"
EDGE_NORMAL   = "#D0D3D4"

TOPIC_PALETTE = {
    "kidney_basics":   "#AED6F1",
    "adpkd_genetics":  "#F9E79F",
    "adpkd_diagnosis": "#A9DFBF",
}
TOPIC_LABELS = {
    "kidney_basics":   "Kidney Basics",
    "adpkd_genetics":  "ADPKD Genetics",
    "adpkd_diagnosis": "Genetic Testing",
}

# ---------------------------------------------------------------------------
# Real content from the prototype (actual questions from modules.json)
# ---------------------------------------------------------------------------
PATIENT_STATE = {
    "kidney_basics":    0.45,
    "adpkd_genetics":   0.18,
    "adpkd_diagnosis":  0.22,
}
PATIENT_Q = {
    "number": 4,
    "topic":  "adpkd_genetics",
    "text":   ("A patient with ADPKD asks: will my children\n"
               "definitely develop the disease?"),
    "options": {
        "A": "Yes — all children will inherit ADPKD",
        "B": "No — ADPKD skips generations",
        "C": "Each child has a 50% chance of inheriting it",
        "D": "Only male children are at risk",
    },
    "selected":     None,
    "correct_key":  "C",
    "answered":     False,
}

PHYSICIAN_STATE = {
    "kidney_basics":    0.92,
    "adpkd_genetics":   0.61,
    "adpkd_diagnosis":  0.55,
}
PHYSICIAN_Q = {
    "number": 6,
    "topic":  "adpkd_diagnosis",
    "text":   ("A male patient with ADPKD is CKD Stage 4.\n"
               "Is genetic testing still clinically useful?"),
    "options": {
        "A": "Not useful at Stage 4 — treatment options limited",
        "B": "Test urgently to qualify for tolvaptan",
        "C": "Testing will decide if transplant is needed",
        "D": "Yes — informs cascade testing & donor evaluation",
    },
    "selected":     "B",          # wrong answer — triggers AI feedback panel
    "correct_key":  "D",
    "answered":     True,
    # Misconception tag drawn from distractor_misconceptions in modules.json
    "misconception":    "tolvaptan_stage_misapplication",
    # Mock LLM response conditioned on learner role + CKD stage context
    "llm_explanation":  ("Tolvaptan slows early-stage ADPKD cyst growth "
                         "and is not indicated at CKD Stage 4. Even so, "
                         "genetic testing remains valuable: PKD1/PKD2 "
                         "variants inform cascade screening and "
                         "living-donor eligibility assessment."),
    "llm_context":      "Clinician \u00b7 CKD Stage 4",
    # Static explanation kept for reference (shown only when correct answer selected)
    "explanation":  ("Even at advanced CKD, genetic testing informs cascade "
                     "testing of at-risk relatives and living donor eligibility "
                     "evaluation. Tolvaptan is for earlier-stage patients."),
}


# ---------------------------------------------------------------------------
# Drawing helpers (all coordinates in normalised panel space 0..1)
# ---------------------------------------------------------------------------

def _rect(ax, x, y, w, h, fc, ec=None, lw=0.8, r=0.02, z=2, alpha=1.0):
    """Draw a rounded rectangle in normalised axes coordinates."""
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad={r}",
        transform=ax.transAxes,
        facecolor=fc,
        edgecolor=ec if ec else fc,
        linewidth=lw,
        zorder=z,
        alpha=alpha,
        clip_on=False,
    )
    ax.add_patch(p)


def _txt(ax, x, y, s, fs=8, c=TEXT_MAIN, weight="normal",
         ha="left", va="center", ls=1.35, z=4):
    ax.text(x, y, s,
            transform=ax.transAxes,
            fontsize=fs, fontweight=weight, color=c,
            ha=ha, va=va, linespacing=ls, zorder=z)


def _bar(ax, x, y, w, h, pct, color_on, label, pct_label, label_fs=7.0):
    """Draw a labelled mastery progress bar."""
    _txt(ax, x, y + h + 0.008, label, fs=label_fs, c=TEXT_MUTED, va="bottom", weight="bold")
    _rect(ax, x, y, w, h, MASTERY_TRACK, ec=None, r=0.008)
    if pct > 0:
        _rect(ax, x, y, w * pct, h, color_on, ec=None, r=0.008, z=3)
    _txt(ax, x + w + 0.015, y + h / 2, pct_label, fs=7.0, c=TEXT_MUTED, weight="bold")


def _draw_panel(ax, state, q, role_label, accent):
    """
    Draw one complete app panel.

    Parameters
    ----------
    ax          : matplotlib Axes with xlim/ylim = (0,1)
    state       : {topic: P(mastery)}
    q           : question content dict
    role_label  : str header text (right-aligned)
    accent      : str hex — role accent colour
    """
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # ── Panel background ──────────────────────────────────────────────────
    _rect(ax, -0.02, -0.02, 1.04, 1.04, PANEL_BG, ec=BORDER, lw=1.2,
          r=0.025, z=1)

    # ── Header bar ────────────────────────────────────────────────────────
    _rect(ax, -0.02, 0.90, 1.04, 0.12, HEADER_BG, r=0.025, z=3)
    _txt(ax, 0.04, 0.961, "CEDAR-PKD", fs=10, c="#FFFFFF", weight="bold", z=5)
    _txt(ax, 0.96, 0.961, role_label, fs=8, c="#AED6F1", ha="right", z=5)

    # Accent stripe below header
    _rect(ax, -0.02, 0.887, 1.04, 0.018, accent, ec=None, r=0.0, z=4)

    # ── Sidebar ───────────────────────────────────────────────────────────
    sb_w = 0.30
    _rect(ax, -0.02, -0.02, sb_w + 0.02, 0.93, SIDEBAR_BG, ec=BORDER,
          lw=0.5, r=0.025, z=2)

    _txt(ax, sb_w / 2 - 0.01, 0.858, "Progress",
         fs=8, c=HEADER_BG, weight="bold", ha="center", z=4)

    topics    = ["kidney_basics", "adpkd_genetics", "adpkd_diagnosis"]
    bar_top   = 0.740
    bar_h     = 0.038
    bar_gap   = 0.095
    bar_x     = 0.030
    bar_w     = sb_w - 0.090

    for ti, topic in enumerate(topics):
        p      = state[topic]
        color  = MASTERY_ON if p >= 0.80 else MASTERY_OFF
        label  = TOPIC_LABELS[topic]
        if p >= 0.80:
            label += "  [mastered]"
        by = bar_top - ti * bar_gap
        lfs = 6.0 if p >= 0.80 else 7.0
        _bar(ax, bar_x, by, bar_w, bar_h, p, color,
             label, f"{int(p * 100)}%", label_fs=lfs)

    # Divider
    ax.plot([sb_w + 0.01, sb_w + 0.01], [0.02, 0.88],
            color=BORDER, lw=0.6, zorder=3,
            transform=ax.transAxes)

    # Mastered count
    n_mast = sum(1 for p in state.values() if p >= 0.80)
    _rect(ax, 0.03, 0.320, sb_w - 0.060, 0.070,
          MASTERY_TRACK, ec=BORDER, lw=0.5, r=0.015, z=3)
    _txt(ax, sb_w / 2 - 0.01, 0.359,
         f"Mastered: {n_mast}/3\nQ {q['number']} of 15",
         fs=7.0, c=TEXT_MUTED, ha="center", ls=1.5, z=4, weight="bold")

    # ── Main content area ─────────────────────────────────────────────────
    mx  = sb_w + 0.055
    mw  = 1.0 - mx - 0.04

    # Topic tag
    tag_w = 0.28
    tag_h = 0.048
    tag_y = 0.828
    _rect(ax, mx, tag_y, tag_w, tag_h, TOPIC_PALETTE[q["topic"]],
          ec=None, r=0.01, z=3)
    _txt(ax, mx + tag_w / 2, tag_y + tag_h / 2,
         TOPIC_LABELS[q["topic"]], fs=7.0, c=TEXT_MAIN, ha="center", z=4, weight="bold")

    # Question text
    _txt(ax, mx, 0.800, q["text"],
         fs=8.5, c=TEXT_MAIN, weight="bold", va="top", ls=1.4, z=4)

    # Answer buttons
    btn_top = 0.635
    btn_h   = 0.085
    btn_gap = 0.012

    for ki, key in enumerate(["A", "B", "C", "D"]):
        by   = btn_top - ki * (btn_h + btn_gap)
        text = textwrap.fill(q["options"][key], width=38)

        if not q["answered"]:
            fc, ec, tc = BTN_NORMAL, EDGE_NORMAL, TEXT_MAIN
        elif key == q["correct_key"]:
            fc, ec, tc = BTN_CORRECT, EDGE_CORRECT, "#1A5C30"
        elif q.get("selected") == key:          # wrong answer chosen
            fc, ec, tc = "#FDEDEC", "#E74C3C", "#C0392B"
        else:
            fc, ec, tc = BTN_NEUTRAL, "#BBBFC0", TEXT_MUTED

        _rect(ax, mx, by, mw, btn_h, fc, ec=ec, lw=0.9, r=0.012, z=3)
        _txt(ax, mx + 0.018, by + btn_h / 2,
             f"{key}.", fs=7.5, c=tc, weight="bold", z=4)
        _txt(ax, mx + 0.060, by + btn_h / 2,
             text, fs=7.5, c=tc, z=4)

    # ── Post-answer feedback panel ────────────────────────────────────────
    # If the learner chose wrong → AI misconception-targeted explanation.
    # If the learner chose correctly → static domain explanation.
    if q["answered"] and q.get("selected") != q["correct_key"] \
            and "llm_explanation" in q:

        # ── AI-generated misconception panel ─────────────────────────────
        AI_PURPLE = "#8E44AD"
        exp_y = 0.022
        exp_h = 0.192
        _rect(ax, mx, exp_y, mw, exp_h, "#F5EEF8", ec=AI_PURPLE,
              lw=1.0, r=0.012, z=3)

        # Purple header bar
        _rect(ax, mx, exp_y + exp_h - 0.040, mw, 0.040,
              AI_PURPLE, ec=None, r=0.010, z=4)
        # Header bar: AI brand
        _txt(ax, mx + mw / 2, exp_y + exp_h - 0.020,
             "AI  \u00b7  CEDAR-PKD  \u00b7  Misconception Feedback",
             fs=6.5, c="white", weight="bold", va="center", ha="center", z=5)

        # Misconception tag
        misc = q.get("misconception", "").replace("_", " ")
        _txt(ax, mx + 0.016, exp_y + exp_h - 0.056,
             f"Misconception: {misc}",
             fs=6.2, c="#6C3483", weight="bold", va="top", z=4)

        # Word-wrapped explanation text (≤ 3 lines)
        words = q["llm_explanation"].split()
        lines, cur = [], ""
        for w in words:
            if len(cur) + len(w) + 1 > 48:
                lines.append(cur); cur = w
            else:
                cur = (cur + " " + w).strip()
        if cur:
            lines.append(cur)
        for li, line in enumerate(lines[:3]):
            _txt(ax, mx + 0.016,
                 exp_y + exp_h - 0.090 - li * 0.033,
                 line, fs=6.5, c="#4A235A", va="top", z=4)

    elif q["answered"] and "explanation" in q:

        # ── Static correct-answer explanation ─────────────────────────────
        exp_y = 0.025
        exp_h = 0.150
        _rect(ax, mx, exp_y, mw, exp_h, "#EBF5FB", ec="#AED6F1",
              lw=0.8, r=0.012, z=3)
        _txt(ax, mx + 0.018, exp_y + exp_h - 0.020,
             "Explanation", fs=7.0, c="#154360", weight="bold", va="top", z=4)

        words = q["explanation"].split()
        lines, cur = [], ""
        for w in words:
            if len(cur) + len(w) + 1 > 60:
                lines.append(cur); cur = w
            else:
                cur = (cur + " " + w).strip()
        if cur:
            lines.append(cur)
        for li, line in enumerate(lines[:3]):
            _txt(ax, mx + 0.018,
                 exp_y + exp_h - 0.048 - li * 0.036,
                 line, fs=7.0, c="#1A3C5E", va="top", z=4)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    apply_cedar_style()

    fig = plt.figure(figsize=(8.0, 5.0))
    fig.patch.set_facecolor("#E8EAED")

    # Two panel axes, placed explicitly in figure-normalised space
    ax_l = fig.add_axes([0.025, 0.10, 0.455, 0.84])
    ax_r = fig.add_axes([0.520, 0.10, 0.455, 0.84])

    _draw_panel(ax_l, PATIENT_STATE, PATIENT_Q,
                "Patient Mode", "#4C9BE8")
    _draw_panel(ax_r, PHYSICIAN_STATE, PHYSICIAN_Q,
                "Clinician Mode", "#56B29A")

    # Caption below each panel
    fig.text(0.255, 0.085,
             "Patient / Caregiver View\n"
             "Plain-language questions  |  Awaiting response",
             ha="center", va="top", fontsize=8.5, color="#3D3D3D",
             linespacing=1.5)
    fig.text(0.748, 0.085,
             "Healthcare Provider View\n"
             "Clinical terminology  |  Wrong answer \u2192 AI misconception feedback",
             ha="center", va="top", fontsize=8.5, color="#3D3D3D",
             linespacing=1.5)

    save_figure(fig, "fig1_app_screenshot")
    plt.close(fig)
    print("Figure 1 complete.")


if __name__ == "__main__":
    main()
