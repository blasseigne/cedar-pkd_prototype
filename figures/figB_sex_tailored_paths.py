"""
figures/figB_sex_tailored_paths.py
Figure B — Sex-tailored Content Personalisation in CEDAR-PKD

Addresses two DOD PRMRP reviewer concerns:
  Consumer Reviewer: 'Whether the information available will be tailored by
    a patient's gender ... it would be helpful for patients to have information
    tailored to them as specifically as possible.'
  Scientist Reviewer A (Statistical Plan): 'Sex as a biological variable is
    not explicitly addressed.'

Shows that identical IRT item parameters and knowledge states produce
completely different question priority rankings for female vs. male patients
because the recommender applies additive demographic boosts for sex-specific,
family-planning-relevant, and disease-stage-relevant items.

Generation
----------
    python figures/figB_sex_tailored_paths.py
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from figures.style import apply_cedar_style, save_figure, GRAY_LIGHT, GRAY_MED, GRAY_DARK
from models.recommender import _is_eligible, _score_item, BOOST_SEX_SPECIFIC, BOOST_FAMILY_PLANNING, BOOST_DISEASE_STAGE
from simulation.simulate import load_content, run_simulation

# ── Colours ───────────────────────────────────────────────────────────────────
FEMALE_C  = "#E85D8A"   # rose — female patient
MALE_C    = "#3D7EBF"   # steel blue — male patient
BASE_C    = "#BDC3C7"   # gray — base IRT discrimination score
SEX_C     = "#C0392B"   # red — sex-specific boost
FP_C      = "#8E44AD"   # purple — family planning boost
STAGE_C   = "#E67E22"   # orange — CKD stage boost
WHITE     = "#FFFFFF"
CEDAR_DARK = "#2C3E50"

# ── Demographic profiles to compare ──────────────────────────────────────────

FEMALE_PROFILE = {
    "id":             "female_early_family_planning",
    "role":           "patient",
    "sex":            "female",
    "family_planning": True,
    "disease_stage":  2,       # CKD Stage 2 — early disease, family planning relevant
    "theta":          0.0,
    "label":          "Female Patient — CKD Stage 2, Family Planning",
    "color":          FEMALE_C,
}

MALE_PROFILE = {
    "id":             "male_advanced",
    "role":           "patient",
    "sex":            "male",
    "family_planning": False,
    "disease_stage":  4,       # CKD Stage 4 — advanced disease
    "theta":          0.0,
    "label":          "Male Patient — CKD Stage 4, No Family Planning",
    "color":          MALE_C,
}

# Initial knowledge state — identical for both profiles (controls for prior knowledge)
INITIAL_STATE = {
    "kidney_basics":   0.30,
    "adpkd_genetics":  0.30,
    "adpkd_diagnosis": 0.30,
}

# Short display labels for questions (truncated from full text)
Q_LABELS = {
    "q_1_2_01": "ADPKD prevalence (1 in 1,000)",
    "q_1_2_02": "PKD1 & PKD2 causative genes",
    "q_1_2_03": "Extra-renal manifestations",
    "q_1_2_04": "Diagnosis delay & mortality risk",
    "q_1_2_05": "Cyst growth mechanism",
    "q_1_2_06": "Inheritance risk for children",
    "q_1_3_01": "Autosomal dominant inheritance",
    "q_1_3_02": "PKD1 vs. PKD2: disease severity",
    "q_1_3_03": "De novo mutations in ADPKD",
    "q_1_3_04": "Seven ADPKD-associated genes",
    "q_1_3_05": "PKD2 prognosis comparison",
    "q_1_3_06": "Genetic testing value if already diagnosed",
    "q_2_3_01": "PGT indications by patient scenario",
    "q_2_3_02": "Variant of Uncertain Significance (VUS)",
    "q_2_3_03": "Reproductive options with ADPKD",
    "q_2_3_04": "Barriers to genetic testing",
    "q_2_3_05": "IVF/PGT options for young woman",
    "q_2_3_06": "Variant classification system",
    "q_2_3_07": "Genetic testing value at CKD Stage 4-5",
    "q_2_3_08": "ADPKD complications in women",
}


def _score_breakdown(q, a_est, knowledge_state, profile):
    """Return (base, boost_sex, boost_fp, boost_stage) for one item."""
    topic     = q["topic"]
    p_mastery = knowledge_state.get(topic, 0.50)
    base      = (1.0 - p_mastery) * float(a_est)
    tags      = q.get("demographic_tags", {})
    b_sex = b_fp = b_stage = 0.0

    if tags.get("sex_specific", False):
        if profile.get("sex") in ("female", "male"):
            b_sex = BOOST_SEX_SPECIFIC

    if tags.get("family_planning_relevant", False):
        if profile.get("family_planning", False):
            b_fp = BOOST_FAMILY_PLANNING

    stage_list = tags.get("disease_stage_relevant", [])
    if stage_list:
        user_stage = profile.get("disease_stage")
        if user_stage is not None and int(user_stage) in [int(s) for s in stage_list]:
            b_stage = BOOST_DISEASE_STAGE

    return base, b_sex, b_fp, b_stage


def _build_ranked_data(questions, irt_dict, profile, top_n=8):
    """Return a DataFrame with ranked questions and score components."""
    rows = []
    for q in questions:
        if not _is_eligible(q, profile):
            continue
        a_est = float(irt_dict.get(q["id"], {}).get("a_estimated", 1.0))
        base, b_sex, b_fp, b_stage = _score_breakdown(q, a_est, INITIAL_STATE, profile)
        total = base + b_sex + b_fp + b_stage
        rows.append({
            "qid":     q["id"],
            "label":   Q_LABELS.get(q["id"], q["id"]),
            "base":    base,
            "b_sex":   b_sex,
            "b_fp":    b_fp,
            "b_stage": b_stage,
            "total":   total,
        })
    df = pd.DataFrame(rows).sort_values("total", ascending=False).head(top_n)
    df = df[::-1]   # reverse for horizontal bar (lowest at bottom)
    return df


def _draw_panel(ax, df, profile, title):
    """Draw a single horizontal stacked bar panel for one profile."""
    color  = profile["color"]
    y_pos  = np.arange(len(df))

    bars_base  = ax.barh(y_pos, df["base"],  color=BASE_C, height=0.55, label="Base (IRT discrimination × topic gap)")
    bars_sex   = ax.barh(y_pos, df["b_sex"], left=df["base"],
                         color=SEX_C,   height=0.55, label=f"+Sex-specific ({BOOST_SEX_SPECIFIC:.2f})")
    bars_fp    = ax.barh(y_pos, df["b_fp"],  left=df["base"] + df["b_sex"],
                         color=FP_C,    height=0.55, label=f"+Family planning ({BOOST_FAMILY_PLANNING:.2f})")
    bars_stage = ax.barh(y_pos, df["b_stage"], left=df["base"] + df["b_sex"] + df["b_fp"],
                         color=STAGE_C, height=0.55, label=f"+CKD stage match ({BOOST_DISEASE_STAGE:.2f})")

    # Total score labels
    for i, row in enumerate(df.itertuples()):
        ax.text(row.total + 0.02, i, f"{row.total:.2f}",
                va="center", fontsize=6.5, color=CEDAR_DARK)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(df["label"], fontsize=7.0)
    ax.set_xlabel("Recommender Score", fontsize=7.5)
    ax.set_xlim(0, 2.4)
    ax.set_title(title, fontsize=8.5, fontweight="bold", color=color, pad=5)

    # Highlight bars with any demographic boost
    boosted_mask = (df["b_sex"] + df["b_fp"] + df["b_stage"]) > 0
    for i, (_, row) in enumerate(df.iterrows()):
        total_boost = row["b_sex"] + row["b_fp"] + row["b_stage"]
        if total_boost > 0:
            ax.get_yticklabels()[i].set_fontweight("bold")
            ax.get_yticklabels()[i].set_color(color)

    # Vertical reference line — top score without any boost
    max_base = df["base"].max()
    ax.axvline(max_base, color=GRAY_MED, lw=0.8, linestyle=":",
               label=f"Max base score (no boost) = {max_base:.2f}")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.25, linestyle="--", linewidth=0.5)


def main():
    apply_cedar_style()

    out_dir = os.path.join(_ROOT, "outputs")
    irt_csv = os.path.join(out_dir, "irt_params.csv")
    if not os.path.exists(irt_csv):
        print("  irt_params.csv not found — running simulation first...")
        run_simulation(verbose=False)

    modules_data, _ = load_content()
    questions = modules_data["questions"]

    irt_df  = pd.read_csv(irt_csv)
    irt_dict = {
        row["question_id"]: {
            "a_estimated": row["a_estimated"],
            "b_estimated": row["b_estimated"],
        }
        for _, row in irt_df.iterrows()
    }

    df_female = _build_ranked_data(questions, irt_dict, FEMALE_PROFILE, top_n=8)
    df_male   = _build_ranked_data(questions, irt_dict, MALE_PROFILE,   top_n=8)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 4.8), sharey=False)

    _draw_panel(ax1, df_female, FEMALE_PROFILE,
                "Female Patient · CKD Stage 2\nFamily planning = Yes")
    _draw_panel(ax2, df_male, MALE_PROFILE,
                "Male Patient · CKD Stage 4\nFamily planning = No")

    # Shared legend from ax1
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2,
               fontsize=6.5, framealpha=0.9,
               bbox_to_anchor=(0.5, -0.04), borderpad=0.6)

    fig.suptitle(
        "Figure B  —  Sex and Demographic Tailoring in CEDAR-PKD\n"
        "Same θ (ability = 0.0) · Same initial knowledge state · Different recommended question priority",
        fontsize=8.5, fontweight="bold", y=1.02,
    )

    plt.tight_layout(pad=0.6)
    save_figure(fig, "figB_sex_tailored_paths")
    plt.close(fig)
    print("Figure B complete.")


if __name__ == "__main__":
    main()
