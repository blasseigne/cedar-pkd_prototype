"""
figures/fig4_taxonomy.py
Figure 4 — CEDAR-PKD Learning Objectives Taxonomy

A structured, hierarchical table mapping all 16 learning objectives across
three ADPKD modules to their:
  • Bloom's taxonomy level (cognitive depth)
  • Estimated IRT difficulty tier (from 2PL model in Session 2)
  • Target audience (patient/care partner vs. physician vs. both)
  • Demographic relevance tags (sex-specific, family-planning)

Reviewer concerns addressed:
    NIH Critique 1 (Moderate): "No learning objectives taxonomy defined."
    NIH Critique 1 (Moderate): "No content recommendation algorithm defined."
    NIH Critique 2: "No demographic variables incorporated."
    DOD Scientist B: "The development of CEDAR-PKD does not seem
        exciting/necessary..." — addresses by showing structured depth.

Usage: python figures/fig4_taxonomy.py   (run from project root)
"""

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from figures.style import (apply_cedar_style, save_figure,
                            BLOOMS_COLORS, TOPIC_COLORS, GRAY_LIGHT, GRAY_MED)
from simulation.simulate import run_simulation


# ---------------------------------------------------------------------------
# Learning objectives with Bloom's level — explicitly assigned by verb
# ---------------------------------------------------------------------------
# Each entry: (module_id, objective_text_short, blooms_level, audience_tag)
# audience_tag: "P" = patient/care partner, "Phy" = physician, "Both"
# Bloom's inferred from objective verb:
#   remember   = Define, Name, Identify, Recognize, List
#   understand = Describe, Explain, Distinguish, Summarize, Understand
#   apply      = Apply, Evaluate, Use, Calculate, Demonstrate

OBJECTIVES = [
    # ── Module 1.2 — Overview of ADPKD ─────────────────────────────────────
    ("mod_1_2", "Define ADPKD and describe its prevalence (~1:1,000)",
     "remember",   "Both"),
    ("mod_1_2", "Identify the primary ADPKD genes (PKD1, PKD2 + 5 others)",
     "remember",   "Both"),
    ("mod_1_2", "Describe major complications beyond kidney failure",
     "understand", "Both"),
    ("mod_1_2", "Explain why early diagnosis and genetic testing matter",
     "understand", "Both"),
    ("mod_1_2", "Distinguish ADPKD from other cystic kidney diseases",
     "understand", "Phy"),

    # ── Module 1.3 — ADPKD Genetics ─────────────────────────────────────────
    ("mod_1_3", "Explain autosomal dominant inheritance (50% transmission)",
     "understand", "Both"),
    ("mod_1_3", "Name all 7 ADPKD genes and relative frequency",
     "remember",   "Phy"),
    ("mod_1_3", "Describe what a pathogenic variant means in ADPKD",
     "understand", "Both"),
    ("mod_1_3", "Explain PKD1 vs. PKD2 differences in disease severity",
     "understand", "Both"),
    ("mod_1_3", "Recognize that de novo variants occur in ~5–10% of cases",
     "remember",   "Phy"),

    # ── Module 2.3 — Genetic Testing for ADPKD ───────────────────────────────
    ("mod_2_3", "Identify clinical indications for ADPKD genetic testing",
     "remember",   "Phy"),
    ("mod_2_3", "Explain variant classification (P / LP / VUS / LB / B)",
     "understand", "Both"),
    ("mod_2_3", "Describe implications for family members; cascade testing",
     "understand", "Both"),
    ("mod_2_3", "Understand reproductive options (PGT-IVF, prenatal testing)",
     "understand", "P"),
    ("mod_2_3", "Recognize barriers to testing and strategies to address them",
     "remember",   "Phy"),
    ("mod_2_3", "Apply variant classification to real clinical scenarios",
     "apply",      "Phy"),
]

# Demographic relevance (manually assigned based on content)
# (sex_specific, family_planning)
DEMO_FLAGS = [
    (False, False),  # mod_1_2 obj 1
    (False, False),  # mod_1_2 obj 2
    (False, False),  # mod_1_2 obj 3
    (False, False),  # mod_1_2 obj 4
    (False, False),  # mod_1_2 obj 5
    (False, True),   # mod_1_3 obj 1 — inheritance affects family planning
    (False, False),  # mod_1_3 obj 2
    (False, False),  # mod_1_3 obj 3
    (False, True),   # mod_1_3 obj 4 — PKD1/PKD2 relevant to severity for family
    (False, True),   # mod_1_3 obj 5 — de novo variants affect family planning
    (False, True),   # mod_2_3 obj 1
    (False, True),   # mod_2_3 obj 2 — VUS classification affects family decisions
    (False, True),   # mod_2_3 obj 3
    (True,  True),   # mod_2_3 obj 4 — reproductive options: sex-specific + family
    (False, False),  # mod_2_3 obj 5
    (False, True),   # mod_2_3 obj 6
]

MODULE_INFO = {
    "mod_1_2": ("Module 1.2", "Overview of ADPKD",      "kidney_basics"),
    "mod_1_3": ("Module 1.3", "ADPKD Genetics",          "adpkd_genetics"),
    "mod_2_3": ("Module 2.3", "Genetic Testing for ADPKD", "adpkd_diagnosis"),
}

BLOOMS_DISPLAY = {
    "remember":   "Remember",
    "understand": "Understand",
    "apply":      "Apply",
}

AUDIENCE_DISPLAY = {
    "Both": "Both",
    "P":    "Patient",
    "Phy":  "Physician",
}

AUDIENCE_COLORS = {
    "Both":      "#A9DFBF",
    "Patient":   "#AED6F1",
    "Physician": "#F9E79F",
}


def make_fig4(data):
    apply_cedar_style()

    irt_df = data["irt_params_df"]

    # Pre-compute average b_estimated per (module_id, blooms_level) for tier label
    avg_b = (
        irt_df.groupby(["module_id", "blooms_level"])["b_estimated"]
        .mean()
        .to_dict()
    )

    def get_tier(module_id, blooms):
        b = avg_b.get((module_id, blooms), 0.0)
        if b < -0.5:  return "Easy"
        elif b <= 0.5: return "Medium"
        else:          return "Hard"

    TIER_COLORS_MAP = {
        "Easy":   "#27AE60",
        "Medium": "#2980B9",
        "Hard":   "#E74C3C",
    }

    # ── Layout constants ───────────────────────────────────────────────────
    n_obj   = len(OBJECTIVES)
    n_cols  = 6   # Module | Objective | Bloom's | Avg Difficulty | Audience | Demo
    col_w   = [0.095, 0.455, 0.105, 0.105, 0.09, 0.105]  # must sum ~= 0.955
    col_headers = ["Module", "Learning Objective",
                   "Bloom's Level", "Avg Difficulty\n(IRT b tier)",
                   "Audience", "Demo Tags"]

    row_h  = 1.0 / (n_obj + 2.5)
    fig_h  = 6.2   # sized so 16-obj table fills the figure cleanly

    fig, ax = plt.subplots(figsize=(7.0, fig_h))
    plt.subplots_adjust(left=0, right=0.955, top=0.93, bottom=0.09)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    x_starts = [0]
    for w in col_w[:-1]:
        x_starts.append(x_starts[-1] + w)

    # ── Column headers ─────────────────────────────────────────────────────
    ax.add_patch(mpatches.FancyBboxPatch(
        (0, 1.0 - row_h), 0.955, row_h,
        boxstyle="square,pad=0", lw=0,
        facecolor="#2C3E50", transform=ax.transAxes,
    ))
    for header, x, w in zip(col_headers, x_starts, col_w):
        ax.text(x + w / 2, 1.0 - row_h / 2,
                header, ha="center", va="center",
                fontsize=6.0, fontweight="bold", color="white",
                transform=ax.transAxes, linespacing=1.3)

    # ── Data rows ──────────────────────────────────────────────────────────
    topic_bg = {
        "kidney_basics":    TOPIC_COLORS["kidney_basics"]    + "66",
        "adpkd_genetics":   TOPIC_COLORS["adpkd_genetics"]   + "66",
        "adpkd_diagnosis":  TOPIC_COLORS["adpkd_diagnosis"]  + "66",
    }

    current_module = None
    module_row_start = None

    for r, ((mod_id, obj_text, blooms, audience), (sex_sp, fam_pl)) in \
            enumerate(zip(OBJECTIVES, DEMO_FLAGS)):

        mod_short, mod_title, topic = MODULE_INFO[mod_id]
        tier   = get_tier(mod_id, blooms)
        y_top  = 1.0 - row_h * (r + 2)
        y_mid  = y_top + row_h / 2

        # Row background (topic-color)
        ax.add_patch(mpatches.FancyBboxPatch(
            (0, y_top), 0.955, row_h,
            boxstyle="square,pad=0", lw=0,
            facecolor=topic_bg[topic], transform=ax.transAxes,
        ))

        # Module label — only on first row of each module block
        if mod_id != current_module:
            current_module = mod_id
            # Count rows in this module
            n_in_mod = sum(1 for o in OBJECTIVES if o[0] == mod_id)
            ax.text(
                x_starts[0] + col_w[0] / 2,
                y_mid,
                f"{mod_short}\n{mod_title}",
                ha="center", va="center",
                fontsize=5.5, fontweight="bold",
                color="#1A252F", linespacing=1.3,
                transform=ax.transAxes,
            )
        else:
            # Lighter separator line within module
            ax.plot([0, 0.955], [y_top + row_h, y_top + row_h],
                    color=GRAY_MED, lw=0.25, transform=ax.transAxes)

        # Module block border (left edge)
        # Draw full module block border on the first row
        if mod_id != getattr(make_fig4, "_last_mod", None):
            make_fig4._last_mod = mod_id

        # ── Objective text ─────────────────────────────────────────────────
        ax.text(
            x_starts[1] + 0.005, y_mid,
            obj_text,
            ha="left", va="center",
            fontsize=5.8, color="#1A252F",
            transform=ax.transAxes,
        )

        # ── Bloom's level pill ─────────────────────────────────────────────
        bx = x_starts[2] + col_w[2] / 2
        ax.add_patch(mpatches.FancyBboxPatch(
            (bx - col_w[2] * 0.44, y_mid - row_h * 0.30),
            col_w[2] * 0.88, row_h * 0.60,
            boxstyle="round,pad=0.003",
            facecolor=BLOOMS_COLORS[blooms],
            edgecolor=GRAY_MED, lw=0.3,
            transform=ax.transAxes,
        ))
        ax.text(bx, y_mid, BLOOMS_DISPLAY[blooms],
                ha="center", va="center",
                fontsize=5.2, fontweight="bold",
                color="#1A252F", transform=ax.transAxes)

        # ── Avg difficulty tier ────────────────────────────────────────────
        ax.text(
            x_starts[3] + col_w[3] / 2, y_mid,
            tier, ha="center", va="center",
            fontsize=6.0, fontweight="bold",
            color=TIER_COLORS_MAP[tier],
            transform=ax.transAxes,
        )

        # ── Audience pill ──────────────────────────────────────────────────
        aud_full = AUDIENCE_DISPLAY[audience]
        ax.add_patch(mpatches.FancyBboxPatch(
            (x_starts[4] + col_w[4] * 0.05,
             y_mid - row_h * 0.30),
            col_w[4] * 0.90, row_h * 0.60,
            boxstyle="round,pad=0.003",
            facecolor=AUDIENCE_COLORS[aud_full],
            edgecolor=GRAY_MED, lw=0.3,
            transform=ax.transAxes,
        ))
        ax.text(x_starts[4] + col_w[4] / 2, y_mid,
                aud_full, ha="center", va="center",
                fontsize=5.2, color="#1A252F",
                transform=ax.transAxes)

        # ── Demo tags ──────────────────────────────────────────────────────
        tags = []
        if sex_sp:  tags.append("♀ sex")
        if fam_pl:  tags.append("♦ family")
        tag_str = "\n".join(tags) if tags else "—"
        ax.text(
            x_starts[5] + col_w[5] / 2, y_mid,
            tag_str, ha="center", va="center",
            fontsize=5.0, color="#555555", linespacing=1.3,
            transform=ax.transAxes,
        )

    # ── Module block dividers (horizontal lines between modules) ──────────
    module_ids  = [o[0] for o in OBJECTIVES]
    for r in range(1, n_obj):
        if module_ids[r] != module_ids[r - 1]:
            y_line = 1.0 - row_h * (r + 2) + row_h
            ax.plot([0, 0.955], [y_line, y_line],
                    color="#2C3E50", lw=1.0,
                    transform=ax.transAxes)

    # Outer border
    border = mpatches.FancyBboxPatch(
        (0, 1.0 - row_h * (n_obj + 2)), 0.955, row_h * (n_obj + 1),
        boxstyle="square,pad=0",
        facecolor="none", edgecolor="#2C3E50", lw=0.8,
        transform=ax.transAxes,
    )
    ax.add_patch(border)

    # ── Legend ─────────────────────────────────────────────────────────────
    topic_patches = [
        mpatches.Patch(facecolor=TOPIC_COLORS["kidney_basics"]    + "66",
                       edgecolor=GRAY_MED, lw=0.4, label="Kidney Basics (Mod 1.2)"),
        mpatches.Patch(facecolor=TOPIC_COLORS["adpkd_genetics"]   + "66",
                       edgecolor=GRAY_MED, lw=0.4, label="ADPKD Genetics (Mod 1.3)"),
        mpatches.Patch(facecolor=TOPIC_COLORS["adpkd_diagnosis"]  + "66",
                       edgecolor=GRAY_MED, lw=0.4, label="Genetic Testing (Mod 2.3)"),
    ]
    tier_patches = [
        mpatches.Patch(facecolor="white", edgecolor=TIER_COLORS_MAP[t],
                       lw=1.2, label=t)
        for t in ["Easy", "Medium", "Hard"]
    ]

    leg1 = fig.legend(handles=topic_patches,
                      title="Topic area",     title_fontsize=5.5,
                      fontsize=5.5,           loc="lower left",
                      bbox_to_anchor=(0.0, 0.0), ncol=3, framealpha=0.9)
    fig.legend(handles=tier_patches,
               title="IRT difficulty tier", title_fontsize=5.5,
               fontsize=5.5,               loc="lower right",
               bbox_to_anchor=(0.955, 0.0), ncol=3, framealpha=0.9)
    fig.add_artist(leg1)

    fig.suptitle(
        "Figure 4.  CEDAR-PKD Learning Objectives Taxonomy\n"
        "Bloom's level and IRT difficulty tier (avg. estimated b) per learning objective "
        "across 3 ADPKD modules. ♦ = family-planning relevant; ♀ = sex-specific content.",
        fontsize=6.2, y=1.01, linespacing=1.5,
    )

    save_figure(fig, "fig4_taxonomy")
    plt.close(fig)
    print("Figure 4 saved.")


if __name__ == "__main__":
    data = run_simulation(verbose=False)
    make_fig4(data)
