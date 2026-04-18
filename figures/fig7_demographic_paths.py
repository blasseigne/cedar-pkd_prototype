"""
figures/fig7_demographic_paths.py
Figure 7 — Demographically-Tailored Learning Paths (swim-lane diagram)

A horizontal swim-lane diagram showing the 10-item adaptive learning path
generated for each of the three CEDAR-PKD demographic profiles:

  • Female Patient — Early Stage, Family Planning
  • Male Patient   — Advanced Stage (CKD 4)
  • Treating Physician

Each lane is a row of 10 coloured cells — one per recommended question slot.
Cell colour encodes topic area.  The question's abbreviated text and a small
demographic-tag badge (♀ sex-specific, ♦ family-planning, ▲ stage-relevant)
appear inside each cell.

This figure directly addresses the NIH and DOD reviewer concerns that
CEDAR-PKD lacked demographic variables and sex/gender-tailored content.

Generation
----------
    python figures/fig7_demographic_paths.py
"""

import os
import sys
import textwrap

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

# ── path setup ────────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from figures.style import (
    apply_cedar_style, save_figure,
    DEMO_COLORS, TOPIC_COLORS,
    GRAY_LIGHT, GRAY_MED, GRAY_DARK,
)
from models.recommender  import generate_learning_path
from simulation.simulate import load_content, run_simulation

import matplotlib as mpl

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
N_ITEMS   = 10
SEED      = 42

PROFILE_ORDER = [
    "female_early_family_planning",
    "male_advanced",
    "treating_physician",
]

TOPIC_DISPLAY = {
    "kidney_basics":    "Kidney\nBasics",
    "adpkd_genetics":   "ADPKD\nGenetics",
    "adpkd_diagnosis":  "Genetic\nTesting",
}

# Brighter topic fill colours for the cells (slightly darkened for legibility)
CELL_COLORS = {
    "kidney_basics":   "#7EC8E3",   # medium sky blue
    "adpkd_genetics":  "#F5C842",   # golden yellow
    "adpkd_diagnosis": "#6FBF8E",   # medium green
}

# Short question labels (≤ 40 chars) — keyed by question id
SHORT_LABELS = {
    "q_1_2_01": "ADPKD prevalence",
    "q_1_2_02": "Primary ADPKD genes",
    "q_1_2_03": "Extra-renal complications",
    "q_1_2_04": "Diagnostic delay & mortality",
    "q_1_2_05": "How cysts reduce function",
    "q_1_2_06": "50% inheritance risk",
    "q_1_3_01": "Meaning of 'dominant'",
    "q_1_3_02": "PKD1 vs PKD2 severity",
    "q_1_3_03": "De novo variants",
    "q_1_3_04": "Seven ADPKD genes",
    "q_1_3_05": "PKD2 slower disease",
    "q_1_3_06": "Value of genetic testing",
    "q_2_3_01": "Indications for testing",
    "q_2_3_02": "VUS interpretation",
    "q_2_3_03": "Cascade testing of siblings",
    "q_2_3_04": "Barriers to testing (MDs)",
    "q_2_3_05": "Preimplantation genetic test",
    "q_2_3_06": "5-tier variant classification",
    "q_2_3_07": "Late-stage testing value",
    "q_2_3_08": "Liver cysts in women",
}

# Demographic tag badges
def _badges(question):
    tags  = question.get("demographic_tags", {})
    parts = []
    if tags.get("sex_specific", False):
        parts.append("♀")
    if tags.get("family_planning_relevant", False):
        parts.append("♦")
    if tags.get("disease_stage_relevant", []):
        parts.append("▲")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    apply_cedar_style()

    # ── Load data ─────────────────────────────────────────────────────────
    out_dir = os.path.join(_ROOT, "outputs")
    irt_csv = os.path.join(out_dir, "irt_params.csv")
    if not os.path.exists(irt_csv):
        print("  irt_params.csv not found — running simulation first...")
        run_simulation(verbose=False)

    modules_data, profiles_data = load_content()
    questions  = modules_data["questions"]
    bkt_params = profiles_data["bkt_default_params"]
    demo_profs = {p["id"]: p for p in profiles_data["demographic_profiles"]}

    irt_df  = pd.read_csv(irt_csv)
    irt_dict = {
        row["question_id"]: {
            "a_estimated": row["a_estimated"],
            "b_estimated": row["b_estimated"],
        }
        for _, row in irt_df.iterrows()
    }

    # ── Generate adaptive paths ────────────────────────────────────────────
    paths = {}
    for pid in PROFILE_ORDER:
        prof  = demo_profs[pid]
        path, states, resps = generate_learning_path(
            questions,
            irt_dict,
            prof["initial_knowledge_state"],
            prof,
            bkt_params,
            n_items = N_ITEMS,
            rng     = np.random.default_rng(SEED),
        )
        paths[pid] = path

    # ── Layout constants ───────────────────────────────────────────────────
    n_rows     = len(PROFILE_ORDER)
    n_cols     = N_ITEMS
    cell_w     = 1.20   # width per cell (data units)
    cell_h     = 1.00   # height per cell
    row_gap    = 0.30   # vertical gap between lanes
    label_w    = 2.80   # left margin for profile labels

    fig_w = label_w + n_cols * cell_w + 0.6
    fig_h = n_rows * (cell_h + row_gap) + 2.0   # extra for 2-row legend + title

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_aspect("equal")
    ax.axis("off")

    ax.set_xlim(0, label_w + n_cols * cell_w + 0.4)
    ax.set_ylim(-0.90, n_rows * (cell_h + row_gap) + 0.8)

    # ── Draw column header numbers ────────────────────────────────────────
    y_header = n_rows * (cell_h + row_gap) + 0.20
    for col in range(n_cols):
        x_mid = label_w + col * cell_w + cell_w / 2
        ax.text(x_mid, y_header, str(col + 1),
                ha="center", va="center", fontsize=7,
                color=GRAY_DARK, fontweight="bold")

    ax.text(label_w + (n_cols * cell_w) / 2, y_header + 0.35,
            "Recommended Item Slot",
            ha="center", va="center", fontsize=8, color=GRAY_DARK)

    # ── Draw lanes ────────────────────────────────────────────────────────
    for row_i, pid in enumerate(PROFILE_ORDER):
        prof      = demo_profs[pid]
        path      = paths[pid]
        row_color = DEMO_COLORS[pid]

        # y base (bottom of this row's cells), rows drawn bottom → top
        y_base = (n_rows - 1 - row_i) * (cell_h + row_gap)

        # Profile label on the left
        ax.text(
            label_w - 0.12, y_base + cell_h / 2,
            prof["display_name"],
            ha="right", va="center",
            fontsize=7.5, fontweight="bold",
            color=row_color,
            wrap=True,
        )

        # Lane background
        lane_bg = FancyBboxPatch(
            (label_w - 0.05, y_base - 0.08),
            n_cols * cell_w + 0.10, cell_h + 0.16,
            boxstyle="round,pad=0.04",
            linewidth=0.8, edgecolor=row_color,
            facecolor=mpl.colors.to_rgba(row_color, 0.06),
        )
        ax.add_patch(lane_bg)

        # Individual question cells
        for col, q in enumerate(path):
            x_left = label_w + col * cell_w
            topic  = q["topic"]
            fill   = CELL_COLORS[topic]
            label  = SHORT_LABELS.get(q["id"], q["id"])
            badges = _badges(q)

            cell = FancyBboxPatch(
                (x_left + 0.04, y_base + 0.04),
                cell_w - 0.08, cell_h - 0.08,
                boxstyle="round,pad=0.03",
                linewidth=0.6,
                edgecolor=mpl.colors.to_rgba(row_color, 0.55),
                facecolor=fill,
            )
            ax.add_patch(cell)

            # Question short label (wrapped)
            ax.text(
                x_left + cell_w / 2, y_base + cell_h * 0.57,
                label,
                ha="center", va="center",
                fontsize=5.6, color="#1A1A2E",
                wrap=False,
            )

            # Badge line (sex ♀ / family ♦ / stage ▲)
            if badges:
                ax.text(
                    x_left + cell_w / 2, y_base + cell_h * 0.22,
                    badges,
                    ha="center", va="center",
                    fontsize=6.5, color="#444444",
                )

    # ── Legend (two rows: topic colours on top, badges below) ────────────
    tot_width = n_cols * cell_w
    leg_y1    = -0.30   # topic row y-centre
    leg_y2    = -0.66   # badge row y-centre
    legend_x  = label_w

    # Topic colour swatches (evenly spaced across full width)
    topic_spacing = tot_width / len(CELL_COLORS)
    for ti, (topic, color) in enumerate(CELL_COLORS.items()):
        x = legend_x + ti * topic_spacing
        rect = FancyBboxPatch(
            (x, leg_y1 - 0.14), 0.26, 0.26,
            boxstyle="round,pad=0.02",
            facecolor=color, edgecolor="#888888", linewidth=0.5,
        )
        ax.add_patch(rect)
        ax.text(x + 0.34, leg_y1,
                TOPIC_DISPLAY[topic].replace("\n", " "),
                ha="left", va="center", fontsize=6.5, color=GRAY_DARK)

    # Badge legend (three items across same width)
    badge_items = [
        ("♀", "Sex-specific content"),
        ("♦", "Family-planning relevant"),
        ("▲", "Disease-stage specific"),
    ]
    badge_spacing = tot_width / len(badge_items)
    for bi, (sym, desc) in enumerate(badge_items):
        bx = legend_x + bi * badge_spacing
        ax.text(bx, leg_y2, f"{sym}  {desc}",
                ha="left", va="center",
                fontsize=6.5, color=GRAY_DARK)

    # ── Title ─────────────────────────────────────────────────────────────
    ax.text(
        (label_w + n_cols * cell_w) / 2, n_rows * (cell_h + row_gap) + 0.75,
        "Figure 7 — Demographically-Tailored Adaptive Learning Paths\n"
        "10-item CEDAR-PKD recommendation paths per demographic profile  "
        "(badges: ♀ sex-specific  ♦ family-planning  ▲ stage-relevant)",
        ha="center", va="center", fontsize=8.5, fontweight="bold",
        color="#1A1A2E",
    )

    plt.tight_layout()
    save_figure(fig, "fig7_demographic_paths")
    plt.close(fig)
    print("Figure 7 complete.")


if __name__ == "__main__":
    main()
