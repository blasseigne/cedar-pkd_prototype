"""
figures/fig2_icc.py
Figure 2 — Item Characteristic Curves (2PL IRT model)

Three-panel figure, one panel per ADPKD learning module.
Each panel shows ICC curves for 3 representative items spanning easy /
medium / hard difficulty, plotted from the MLE-estimated 2PL parameters.

Reviewer concern addressed:
    NIH Critique 1 (Moderate): "The proposal does not define the IRT model
    (1PL, 2PL, or 3PL), the content recommendation algorithm, or the
    learning objectives taxonomy. Without this, it is unclear how the
    ALE's adaptive logic would be validated."

Usage: python figures/fig2_icc.py   (run from project root)
"""

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches

from figures.style import apply_cedar_style, save_figure, TOPIC_COLORS, GRAY_MED, THRESHOLD_COLOR
from models.irt import get_icc_data
from simulation.simulate import run_simulation


# ---------------------------------------------------------------------------
# Items to display per panel — selected to span easy/medium/hard difficulty
# ---------------------------------------------------------------------------

PANELS = [
    {
        "module_id":    "mod_1_2",
        "title":        "Module 1.2 — Overview of ADPKD",
        "topic":        "kidney_basics",
        "item_ids":     ["q_1_2_01", "q_1_2_03", "q_1_2_04"],
        "item_labels":  ["1.2-01", "1.2-03", "1.2-04"],
    },
    {
        "module_id":    "mod_1_3",
        "title":        "Module 1.3 — ADPKD Genetics",
        "topic":        "adpkd_genetics",
        "item_ids":     ["q_1_3_01", "q_1_3_04", "q_1_3_03"],
        "item_labels":  ["1.3-01", "1.3-04", "1.3-03"],
    },
    {
        "module_id":    "mod_2_3",
        "title":        "Module 2.3 — Genetic Testing",
        "topic":        "adpkd_diagnosis",
        "item_ids":     ["q_2_3_06", "q_2_3_02", "q_2_3_07"],
        "item_labels":  ["2.3-06", "2.3-02", "2.3-07"],
    },
]

# Colors for Easy / Medium / Hard
TIER_COLORS = {
    "Easy":   "#27AE60",   # green
    "Medium": "#2980B9",   # blue
    "Hard":   "#E74C3C",   # red
}
TIER_STYLES = {
    "Easy":   "-",
    "Medium": "--",
    "Hard":   "-.",
}


def make_fig2(data):
    apply_cedar_style()

    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.8), sharey=True)
    fig.subplots_adjust(wspace=0.08)

    theta_range = (-3.2, 3.2)

    for ax, panel in zip(axes, PANELS):
        topic_color = TOPIC_COLORS[panel["topic"]]

        # Subtle background tint per module topic
        ax.set_facecolor(topic_color + "33")   # 20% alpha hex

        # Reference lines
        ax.axvline(0, color=GRAY_MED, lw=0.8, ls=":", zorder=1, label="_nolegend_")
        ax.axhline(0.5, color=GRAY_MED, lw=0.8, ls=":", zorder=1, label="_nolegend_")

        for qid, label in zip(panel["item_ids"], panel["item_labels"]):
            row = data["irt_params_df"][data["irt_params_df"]["question_id"] == qid].iloc[0]
            a   = row["a_estimated"]
            b   = row["b_estimated"]
            tier = row["difficulty_tier"]

            theta_vals, p_vals = get_icc_data(a, b, theta_range)

            ax.plot(
                theta_vals, p_vals,
                color=TIER_COLORS[tier],
                ls=TIER_STYLES[tier],
                lw=1.6,
                zorder=3,
                label=f"{label}  (b={b:.2f}, a={a:.2f})",
            )

            # Annotate b on the x-axis
            ax.annotate(
                f"b={b:.1f}",
                xy=(b, 0.50),
                xytext=(b + 0.15, 0.38),
                fontsize=5.5,
                color=TIER_COLORS[tier],
                arrowprops=dict(arrowstyle="-", color=TIER_COLORS[tier],
                                lw=0.6),
            )

        ax.set_xlim(theta_range)
        ax.set_ylim(-0.02, 1.02)
        ax.set_xlabel("Learner ability  (θ)", fontsize=7)
        ax.set_title(panel["title"], fontsize=7.5, fontweight="bold", pad=4)
        ax.legend(fontsize=5.5, loc="upper left", framealpha=0.85,
                  handlelength=1.5)

        # θ tick labels only on leftmost panel
        if ax != axes[0]:
            ax.tick_params(labelleft=False)

    axes[0].set_ylabel("P (correct response)", fontsize=7)

    # Shared legend for difficulty tiers at the bottom
    legend_handles = [
        mlines.Line2D([], [], color=TIER_COLORS[t], ls=TIER_STYLES[t],
                      lw=1.6, label=t)
        for t in ["Easy", "Medium", "Hard"]
    ]
    fig.legend(
        handles=legend_handles,
        title="Difficulty tier",
        title_fontsize=6.5,
        fontsize=6,
        loc="lower center",
        ncol=3,
        bbox_to_anchor=(0.5, -0.05),
        framealpha=0.9,
    )

    fig.suptitle(
        "Figure 2.  Item Characteristic Curves — 2-Parameter Logistic (2PL) IRT Model\n"
        "Parameters estimated by item-level MLE from simulated response data (N=100 users, 20 items)",
        fontsize=7, y=1.02,
    )

    save_figure(fig, "fig2_icc")
    plt.close(fig)
    print("Figure 2 saved.")


if __name__ == "__main__":
    data = run_simulation(verbose=False)
    make_fig2(data)
