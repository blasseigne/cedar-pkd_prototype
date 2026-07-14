"""
figures/figD_taxonomy_icc.py
Combined figure — CEDAR-PKD Item Calibration

  A (top):    Learning Objectives Taxonomy — 16 objectives mapped to Bloom's
              level, IRT difficulty tier, audience, and demographic tags
  B (bottom): Item Characteristic Curves — Module 1.3 ADPKD Genetics (one panel),
              representative Easy / Medium / Hard items from the 2PL IRT model

Usage: python figures/figD_taxonomy_icc.py   (run from project root)
"""

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

from figures.style import (apply_cedar_style, save_figure,
                            BLOOMS_COLORS, TOPIC_COLORS, GRAY_MED)
from models.irt import get_icc_data
from simulation.simulate import run_simulation


# ── Learning objectives ───────────────────────────────────────────────────────

OBJECTIVES = [
    ("mod_1_2", "Define ADPKD and describe its prevalence (~1:1,000)",               "remember",   "Both"),
    ("mod_1_2", "Identify the primary ADPKD genes (PKD1, PKD2 + 5 others)",          "remember",   "Both"),
    ("mod_1_2", "Describe major complications beyond kidney failure",                 "understand", "Both"),
    ("mod_1_2", "Explain why early diagnosis and genetic testing matter",             "understand", "Both"),
    ("mod_1_2", "Distinguish ADPKD from other cystic kidney diseases",               "understand", "Phy"),
    ("mod_1_3", "Explain autosomal dominant inheritance (50% transmission)",          "understand", "Both"),
    ("mod_1_3", "Name all 7 ADPKD genes and relative frequency",                     "remember",   "Phy"),
    ("mod_1_3", "Describe what a pathogenic variant means in ADPKD",                 "understand", "Both"),
    ("mod_1_3", "Explain PKD1 vs. PKD2 differences in disease severity",             "understand", "Both"),
    ("mod_1_3", "Recognize that de novo variants occur in ~5–10% of cases",          "remember",   "Phy"),
    ("mod_2_3", "Identify clinical indications for ADPKD genetic testing",           "remember",   "Phy"),
    ("mod_2_3", "Explain variant classification (P / LP / VUS / LB / B)",            "understand", "Both"),
    ("mod_2_3", "Describe implications for family members; cascade testing",          "understand", "Both"),
    ("mod_2_3", "Understand reproductive options (PGT-IVF, prenatal testing)",       "understand", "P"),
    ("mod_2_3", "Recognize barriers to testing and strategies to address them",      "remember",   "Phy"),
    ("mod_2_3", "Apply variant classification to real clinical scenarios",            "apply",      "Phy"),
]

DEMO_FLAGS = [
    (False, False), (False, False), (False, False), (False, False), (False, False),
    (False, True),  (False, False), (False, False), (False, True),  (False, True),
    (False, True),  (False, True),  (False, True),  (True,  True),  (False, False),
    (False, True),
]

MODULE_INFO = {
    "mod_1_2": ("Module 1.2", "Overview of ADPKD",         "kidney_basics"),
    "mod_1_3": ("Module 1.3", "ADPKD Genetics",            "adpkd_genetics"),
    "mod_2_3": ("Module 2.3", "Genetic Testing for ADPKD", "adpkd_diagnosis"),
}

BLOOMS_DISPLAY   = {"remember": "Remember", "understand": "Understand", "apply": "Apply"}
AUDIENCE_DISPLAY = {"Both": "Both", "P": "Patient", "Phy": "Physician"}
AUDIENCE_COLORS  = {"Both": "#A9DFBF", "Patient": "#AED6F1", "Physician": "#F9E79F"}
TIER_COLORS      = {"Easy": "#27AE60", "Medium": "#2980B9", "Hard": "#E74C3C"}
TIER_STYLES      = {"Easy": "-",       "Medium": "--",       "Hard": "-."}

# Single ICC panel — Module 1.3 has the clearest Easy / Medium / Hard spread
ICC_PANEL = {
    "topic":       "adpkd_genetics",
    "title":       "Module 1.3 — ADPKD Genetics",
    "item_ids":    ["q_1_3_01", "q_1_3_04", "q_1_3_03"],
    "item_labels": ["1.3-01",   "1.3-04",   "1.3-03"],
}


# ── Panel A: taxonomy table ───────────────────────────────────────────────────

def draw_taxonomy(ax, irt_df):
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    n_obj = len(OBJECTIVES)
    # Widened module column so labels fit; objective column reduced proportionally
    col_w = [0.13, 0.415, 0.105, 0.105, 0.09, 0.11]
    col_headers = [
        "Module", "Learning Objective",
        "Bloom's Level", "Avg Difficulty\n(IRT b tier)",
        "Audience", "Demo Tags",
    ]
    row_h = 1.0 / (n_obj + 2.5)

    x_starts = [0]
    for w in col_w[:-1]:
        x_starts.append(x_starts[-1] + w)

    avg_b = (
        irt_df.groupby(["module_id", "blooms_level"])["b_estimated"]
        .mean().to_dict()
    )

    def get_tier(mod_id, blooms):
        b = avg_b.get((mod_id, blooms), 0.0)
        if b < -0.5:    return "Easy"
        elif b <= 0.5:  return "Medium"
        else:           return "Hard"

    # Pre-compute module block row ranges for vertical centering of labels
    module_row_ranges = {}
    for r, (mod_id, *_) in enumerate(OBJECTIVES):
        if mod_id not in module_row_ranges:
            module_row_ranges[mod_id] = [r, r]
        else:
            module_row_ranges[mod_id][1] = r

    # Header bar
    ax.add_patch(mpatches.FancyBboxPatch(
        (0, 1.0 - row_h), 0.955, row_h,
        boxstyle="square,pad=0", lw=0,
        facecolor="#2C3E50", transform=ax.transAxes,
    ))
    for header, x, w in zip(col_headers, x_starts, col_w):
        ax.text(x + w / 2, 1.0 - row_h / 2, header,
                ha="center", va="center", fontsize=6.0, fontweight="bold",
                color="white", transform=ax.transAxes, linespacing=1.3)

    topic_bg = {k: TOPIC_COLORS[k] + "66" for k in TOPIC_COLORS}

    current_module = None
    for r, ((mod_id, obj_text, blooms, audience), (sex_sp, fam_pl)) in \
            enumerate(zip(OBJECTIVES, DEMO_FLAGS)):

        mod_short, mod_title, topic = MODULE_INFO[mod_id]
        tier  = get_tier(mod_id, blooms)
        y_top = 1.0 - row_h * (r + 2)
        y_mid = y_top + row_h / 2

        # Row background
        ax.add_patch(mpatches.FancyBboxPatch(
            (0, y_top), 0.955, row_h,
            boxstyle="square,pad=0", lw=0,
            facecolor=topic_bg[topic], transform=ax.transAxes,
        ))

        # Inter-row separator — skip module column so label reads as spanning the block
        if mod_id == current_module:
            ax.plot([x_starts[1], 0.955], [y_top + row_h, y_top + row_h],
                    color=GRAY_MED, lw=0.25, transform=ax.transAxes)
        else:
            current_module = mod_id

        # Objective text — clipped to its column
        ax.text(x_starts[1] + 0.006, y_mid, obj_text,
                ha="left", va="center", fontsize=5.6, color="#1A252F",
                clip_on=True, transform=ax.transAxes)

        # Bloom's pill
        bx = x_starts[2] + col_w[2] / 2
        ax.add_patch(mpatches.FancyBboxPatch(
            (bx - col_w[2] * 0.44, y_mid - row_h * 0.30),
            col_w[2] * 0.88, row_h * 0.60,
            boxstyle="round,pad=0.003",
            facecolor=BLOOMS_COLORS[blooms], edgecolor=GRAY_MED, lw=0.3,
            transform=ax.transAxes,
        ))
        ax.text(bx, y_mid, BLOOMS_DISPLAY[blooms],
                ha="center", va="center", fontsize=5.2, fontweight="bold",
                color="#1A252F", transform=ax.transAxes)

        # Avg difficulty tier
        ax.text(x_starts[3] + col_w[3] / 2, y_mid, tier,
                ha="center", va="center", fontsize=6.0, fontweight="bold",
                color=TIER_COLORS[tier], transform=ax.transAxes)

        # Audience pill
        aud_full = AUDIENCE_DISPLAY[audience]
        ax.add_patch(mpatches.FancyBboxPatch(
            (x_starts[4] + col_w[4] * 0.05, y_mid - row_h * 0.30),
            col_w[4] * 0.90, row_h * 0.60,
            boxstyle="round,pad=0.003",
            facecolor=AUDIENCE_COLORS[aud_full], edgecolor=GRAY_MED, lw=0.3,
            transform=ax.transAxes,
        ))
        ax.text(x_starts[4] + col_w[4] / 2, y_mid, aud_full,
                ha="center", va="center", fontsize=5.2, color="#1A252F",
                transform=ax.transAxes)

        # Demo tags
        tags = []
        if sex_sp:  tags.append("♀ sex")
        if fam_pl:  tags.append("♦ family")
        ax.text(x_starts[5] + col_w[5] / 2, y_mid,
                "\n".join(tags) if tags else "—",
                ha="center", va="center", fontsize=5.0, color="#555555",
                linespacing=1.3, transform=ax.transAxes)

    # Module labels — drawn AFTER rows, vertically centered across each block
    mod_label_text = {
        "mod_1_2": "Module 1.2\nOverview\nof ADPKD",
        "mod_1_3": "Module 1.3\nADPKD\nGenetics",
        "mod_2_3": "Module 2.3\nGenetic\nTesting",
    }
    for mod_id, (r_start, r_end) in module_row_ranges.items():
        y_block_top = 1.0 - row_h * (r_start + 2) + row_h
        y_block_bot = 1.0 - row_h * (r_end + 2)
        y_center    = (y_block_top + y_block_bot) / 2
        ax.text(x_starts[0] + col_w[0] / 2, y_center,
                mod_label_text[mod_id],
                ha="center", va="center", fontsize=5.0, fontweight="bold",
                color="#1A252F", linespacing=1.35, transform=ax.transAxes)

    # Module block dividers
    module_ids = [o[0] for o in OBJECTIVES]
    for r in range(1, n_obj):
        if module_ids[r] != module_ids[r - 1]:
            y_line = 1.0 - row_h * (r + 2) + row_h
            ax.plot([0, 0.955], [y_line, y_line],
                    color="#2C3E50", lw=1.0, transform=ax.transAxes)

    # Outer border
    ax.add_patch(mpatches.FancyBboxPatch(
        (0, 1.0 - row_h * (n_obj + 2)), 0.955, row_h * (n_obj + 1),
        boxstyle="square,pad=0",
        facecolor="none", edgecolor="#2C3E50", lw=0.8,
        transform=ax.transAxes,
    ))

    # Legends inside the ax (below the table)
    topic_patches = [
        mpatches.Patch(facecolor=TOPIC_COLORS["kidney_basics"]   + "66",
                       edgecolor=GRAY_MED, lw=0.4, label="Kidney Basics (Mod 1.2)"),
        mpatches.Patch(facecolor=TOPIC_COLORS["adpkd_genetics"]  + "66",
                       edgecolor=GRAY_MED, lw=0.4, label="ADPKD Genetics (Mod 1.3)"),
        mpatches.Patch(facecolor=TOPIC_COLORS["adpkd_diagnosis"] + "66",
                       edgecolor=GRAY_MED, lw=0.4, label="Genetic Testing (Mod 2.3)"),
    ]
    tier_patches = [
        mpatches.Patch(facecolor="white", edgecolor=TIER_COLORS[t], lw=1.2, label=t)
        for t in ["Easy", "Medium", "Hard"]
    ]

    leg1 = ax.legend(handles=topic_patches,
                     title="Topic area", title_fontsize=5.0, fontsize=5.0,
                     loc="lower left", bbox_to_anchor=(0.0, 0.0),
                     ncol=3, framealpha=0.9)
    ax.add_artist(leg1)
    ax.legend(handles=tier_patches,
              title="IRT difficulty tier", title_fontsize=5.0, fontsize=5.0,
              loc="lower right", bbox_to_anchor=(0.955, 0.0),
              ncol=3, framealpha=0.9)



# ── Panel B: single ICC panel ─────────────────────────────────────────────────

def draw_icc(ax, data):
    panel       = ICC_PANEL
    topic_color = TOPIC_COLORS[panel["topic"]]
    theta_range = (-3.2, 3.2)

    ax.set_facecolor(topic_color + "33")
    ax.axvline(0,   color=GRAY_MED, lw=0.8, ls=":", zorder=1)
    ax.axhline(0.5, color=GRAY_MED, lw=0.8, ls=":", zorder=1)

    for qid, label in zip(panel["item_ids"], panel["item_labels"]):
        row  = data["irt_params_df"][data["irt_params_df"]["question_id"] == qid].iloc[0]
        a, b = row["a_estimated"], row["b_estimated"]
        tier = row["difficulty_tier"]

        theta_vals, p_vals = get_icc_data(a, b, theta_range)
        ax.plot(theta_vals, p_vals,
                color=TIER_COLORS[tier], ls=TIER_STYLES[tier],
                lw=1.6, zorder=3,
                label=f"{label}  (b={b:.2f}, a={a:.2f})")
        ax.annotate(f"b={b:.1f}", xy=(b, 0.50), xytext=(b + 0.15, 0.38),
                    fontsize=5.5, color=TIER_COLORS[tier],
                    arrowprops=dict(arrowstyle="-", color=TIER_COLORS[tier], lw=0.6))

    ax.set_xlim(theta_range)
    ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel("Learner ability  (θ)", fontsize=7)
    ax.set_ylabel("P (correct response)", fontsize=7)
    ax.set_title(panel["title"], fontsize=7.5, fontweight="bold", pad=4)

    # Item legend (upper left)
    item_leg = ax.legend(fontsize=5.5, loc="upper left",
                         framealpha=0.85, handlelength=1.5)
    ax.add_artist(item_leg)

    # Tier legend (lower right)
    tier_handles = [
        mlines.Line2D([], [], color=TIER_COLORS[t], ls=TIER_STYLES[t],
                      lw=1.6, label=t)
        for t in ["Easy", "Medium", "Hard"]
    ]
    ax.legend(handles=tier_handles,
              title="Difficulty tier", title_fontsize=6.0,
              fontsize=5.5, loc="lower right", framealpha=0.85)



# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    apply_cedar_style()
    data = run_simulation(verbose=False)

    fig = plt.figure(figsize=(7.0, 9.2))
    gs  = gridspec.GridSpec(
        2, 1,
        height_ratios=[2.5, 1],
        hspace=0.14,
        left=0.06, right=0.97,
        top=0.97, bottom=0.05,
    )

    ax_top = fig.add_subplot(gs[0])
    ax_bot = fig.add_subplot(gs[1])

    draw_taxonomy(ax_top, data["irt_params_df"])
    draw_icc(ax_bot, data)

    # Panel labels in figure coordinates — same x guarantees alignment
    label_x = ax_top.get_position().x0 - 0.018
    fig.text(label_x, ax_top.get_position().y1 + 0.004, "A",
             fontsize=11, fontweight="bold", va="bottom")
    fig.text(label_x, ax_bot.get_position().y1 + 0.004, "B",
             fontsize=11, fontweight="bold", va="bottom")

    save_figure(fig, "figD_taxonomy_icc")
    plt.close(fig)
    print("Figure D (taxonomy + ICC) saved.")


if __name__ == "__main__":
    main()
