"""
figures/fig3_item_params.py
Figure 3 — Item Parameter Table (2PL IRT estimated parameters)

Renders a grant-quality formatted table showing all 20 CEDAR-PKD quiz items
with their estimated 2PL discrimination (a) and difficulty (b) parameters,
alongside content metadata (module, Bloom's level, audience, demographic tags).

Reviewer concerns addressed:
    NIH Critique 1 (Moderate): IRT model unspecified, no item calibration detail.
    NIH Critique 2: No demographic variables incorporated.
    DOD: Sex/gender tailoring missing.

Usage: python figures/fig3_item_params.py   (run from project root)
"""

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import to_rgba

from figures.style import (apply_cedar_style, save_figure,
                            BLOOMS_COLORS, TOPIC_COLORS, GRAY_LIGHT, GRAY_MED)
from simulation.simulate import run_simulation


# Display labels
BLOOMS_DISPLAY = {
    "remember":   "Remember",
    "understand": "Understand",
    "apply":      "Apply",
}
MODULE_DISPLAY = {
    "mod_1_2": "1.2  Overview",
    "mod_1_3": "1.3  Genetics",
    "mod_2_3": "2.3  Genetic Testing",
}
AUDIENCE_DISPLAY = {
    "both":      "Both",
    "patient":   "Pt",
    "physician": "Phys",
}
TIER_COLORS = {
    "Easy":   "#27AE60",
    "Medium": "#2980B9",
    "Hard":   "#E74C3C",
}


def make_fig3(data):
    apply_cedar_style()

    df = data["irt_params_df"].copy()

    # Shorten question IDs for display
    df["item"] = df["question_id"].str.replace("q_", "").str.replace("_", "-")

    # Demographic tag string
    def demo_tag(row):
        tags = []
        if row["sex_specific"]:
            tags.append("sex")
        if row["family_planning"]:
            tags.append("fam")
        return ", ".join(tags) if tags else "—"
    df["demo"] = df.apply(demo_tag, axis=1)

    # Column definitions
    col_labels  = ["Item", "Module", "Bloom's Level",
                   "Audience", "b prior", "b est.", "a est.", "Tier", "Demo Tags"]
    col_widths  = [0.07, 0.14, 0.11, 0.08, 0.07, 0.07, 0.07, 0.07, 0.10]
    col_keys    = ["item", "module_display", "blooms_display",
                   "audience_display", "b_prior_str", "b_est_str",
                   "a_est_str", "difficulty_tier", "demo"]

    df["module_display"]   = df["module_id"].map(MODULE_DISPLAY)
    df["blooms_display"]   = df["blooms_level"].map(BLOOMS_DISPLAY)
    df["audience_display"] = df["audience"].map(AUDIENCE_DISPLAY)
    df["b_prior_str"]      = df["b_prior"].map(lambda x: f"{x:+.2f}")
    df["b_est_str"]        = df["b_estimated"].map(lambda x: f"{x:+.3f}")
    df["a_est_str"]        = df["a_estimated"].map(lambda x: f"{x:.3f}")

    n_rows = len(df)
    n_cols = len(col_labels)

    fig_h = 0.28 * (n_rows + 2) + 0.6   # dynamic height
    fig, ax = plt.subplots(figsize=(7.0, fig_h))
    ax.axis("off")

    row_h   = 1.0 / (n_rows + 2)
    header_y = 1.0 - row_h * 0.5

    # Cumulative x positions
    x_pos = [0]
    for w in col_widths[:-1]:
        x_pos.append(x_pos[-1] + w)

    # ── Header row ─────────────────────────────────────────────────────────
    ax.add_patch(mpatches.FancyBboxPatch(
        (0, 1.0 - row_h), 1.0, row_h,
        boxstyle="square,pad=0", linewidth=0,
        facecolor="#2C3E50", transform=ax.transAxes,
    ))
    for i, (label, x, w) in enumerate(zip(col_labels, x_pos, col_widths)):
        ax.text(
            x + w / 2, 1.0 - row_h / 2, label,
            ha="center", va="center", fontsize=6.0,
            fontweight="bold", color="white",
            transform=ax.transAxes,
        )

    # ── Data rows ──────────────────────────────────────────────────────────
    topic_bg = {
        "kidney_basics":    TOPIC_COLORS["kidney_basics"]    + "55",
        "adpkd_genetics":   TOPIC_COLORS["adpkd_genetics"]   + "55",
        "adpkd_diagnosis":  TOPIC_COLORS["adpkd_diagnosis"]  + "55",
    }

    for r, (_, row) in enumerate(df.iterrows()):
        y_top = 1.0 - row_h * (r + 2)
        y_mid = y_top + row_h / 2

        # Row background (topic-colored)
        bg = topic_bg.get(row["topic"], GRAY_LIGHT)
        ax.add_patch(mpatches.FancyBboxPatch(
            (0, y_top), 1.0, row_h,
            boxstyle="square,pad=0", linewidth=0,
            facecolor=bg, transform=ax.transAxes,
        ))

        # Thin divider line
        ax.plot([0, 1], [y_top, y_top], color=GRAY_MED, lw=0.3,
                transform=ax.transAxes)

        for i, (key, x, w) in enumerate(zip(col_keys, x_pos, col_widths)):
            val = str(row[key])

            # Bloom's level — colored pill badge
            if key == "blooms_display":
                blooms_key = row["blooms_level"]
                pill_color = BLOOMS_COLORS[blooms_key]
                pill_x = x + w / 2
                ax.add_patch(mpatches.FancyBboxPatch(
                    (pill_x - w * 0.42, y_mid - row_h * 0.30),
                    w * 0.84, row_h * 0.60,
                    boxstyle="round,pad=0.005",
                    facecolor=pill_color,
                    edgecolor=GRAY_MED, lw=0.3,
                    transform=ax.transAxes,
                ))
                ax.text(pill_x, y_mid, val,
                        ha="center", va="center",
                        fontsize=5.5, fontweight="bold",
                        color="#1A252F", transform=ax.transAxes)

            # Difficulty tier — colored text
            elif key == "difficulty_tier":
                ax.text(x + w / 2, y_mid, val,
                        ha="center", va="center",
                        fontsize=6.0, fontweight="bold",
                        color=TIER_COLORS.get(val, "black"),
                        transform=ax.transAxes)

            # b estimated — color by tier
            elif key == "b_est_str":
                tier = row["difficulty_tier"]
                ax.text(x + w / 2, y_mid, val,
                        ha="center", va="center",
                        fontsize=5.8,
                        color=TIER_COLORS.get(tier, "black"),
                        fontweight="bold",
                        transform=ax.transAxes)

            # Default text
            else:
                ax.text(x + w / 2, y_mid, val,
                        ha="center", va="center",
                        fontsize=5.8, color="#1A252F",
                        transform=ax.transAxes)

    # Bottom border
    ax.plot([0, 1], [1.0 - row_h * (n_rows + 2)] * 2,
            color=GRAY_MED, lw=0.8, transform=ax.transAxes)

    # ── Legend for topic-area colors ───────────────────────────────────────
    legend_patches = [
        mpatches.Patch(facecolor=TOPIC_COLORS["kidney_basics"]   + "55",
                       edgecolor=GRAY_MED, lw=0.5, label="Kidney Basics"),
        mpatches.Patch(facecolor=TOPIC_COLORS["adpkd_genetics"]  + "55",
                       edgecolor=GRAY_MED, lw=0.5, label="ADPKD Genetics"),
        mpatches.Patch(facecolor=TOPIC_COLORS["adpkd_diagnosis"] + "55",
                       edgecolor=GRAY_MED, lw=0.5, label="Genetic Testing"),
    ]
    blooms_patches = [
        mpatches.Patch(facecolor=BLOOMS_COLORS["remember"],   edgecolor=GRAY_MED,
                       lw=0.5, label="Remember"),
        mpatches.Patch(facecolor=BLOOMS_COLORS["understand"], edgecolor=GRAY_MED,
                       lw=0.5, label="Understand"),
        mpatches.Patch(facecolor=BLOOMS_COLORS["apply"],      edgecolor=GRAY_MED,
                       lw=0.5, label="Apply"),
    ]
    leg1 = fig.legend(handles=legend_patches, title="Topic area",
                      title_fontsize=5.5, fontsize=5.5,
                      loc="lower left", bbox_to_anchor=(0.01, -0.06),
                      ncol=3, framealpha=0.9)
    fig.legend(handles=blooms_patches, title="Bloom's level",
               title_fontsize=5.5, fontsize=5.5,
               loc="lower right", bbox_to_anchor=(0.99, -0.06),
               ncol=3, framealpha=0.9)
    fig.add_artist(leg1)

    fig.suptitle(
        "Figure 3.  CEDAR-PKD Item Parameters — 2PL IRT Estimates (N = 100 simulated users)\n"
        "b = difficulty (negative = easier); a = discrimination; Demo Tags: sex = sex-specific content, "
        "fam = family-planning relevant",
        fontsize=6.0, y=1.01,
    )

    save_figure(fig, "fig3_item_params")
    plt.close(fig)
    print("Figure 3 saved.")


if __name__ == "__main__":
    data = run_simulation(verbose=False)
    make_fig3(data)
