"""
figures/fig6_adaptive_vs_static.py
Figure 6 — Adaptive vs. Static Knowledge Gain Comparison

Single panel showing cumulative topics mastered (P(mastery) ≥ 0.80) across
20 interactions for all four simulation profiles.  Each profile is shown as
two curves:
  • Solid line   — CEDAR-PKD adaptive ordering (recommender-selected)
  • Dashed line  — Static ordering (fixed sequence through question bank)

Same learner theta, same IRT-simulated responses per item, different ordering.
Demonstrates that adaptive sequencing accelerates mastery relative to static
delivery — directly addressing the reviewer concern about whether
individualised learning actually improves outcomes.

Generation
----------
    python figures/fig6_adaptive_vs_static.py
"""

import json
import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

# ── path setup ────────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from figures.style import (
    apply_cedar_style, save_figure,
    PROFILE_COLORS, ADAPTIVE_COLOR, STATIC_COLOR,
    GRAY_MED, GRAY_DARK, FIG_DOUBLE,
)
from models.bkt         import update_knowledge_state, topics_mastered
from models.recommender import adaptive_next, _is_eligible
from models.irt         import p_correct
from simulation.simulate import load_content, run_simulation

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MASTERY_THRESHOLD = 0.80
N_ITEMS           = 20
SEED              = 42

PROFILE_ORDER = [
    "newly_diagnosed_patient",
    "experienced_patient",
    "primary_care_physician",
    "nephrologist",
]


# ---------------------------------------------------------------------------
# Simulation helpers
# ---------------------------------------------------------------------------

def _pre_generate_responses(profile, questions, irt_dict, seed=SEED):
    """
    Pre-generate a binary response for every question for this profile.
    Both adaptive and static sessions use these same responses so the
    comparison reflects ordering alone, not chance.

    Returns
    -------
    dict {question_id: 0 or 1}
    """
    rng   = np.random.default_rng(seed)
    theta = float(profile["theta"])
    resps = {}
    for q in questions:
        item  = irt_dict.get(q["id"], {})
        a_est = float(item.get("a_estimated", 1.0))
        b_est = float(item.get("b_estimated", 0.0))
        prob  = float(p_correct(theta, a_est, b_est))
        resps[q["id"]] = int(rng.binomial(1, prob))
    return resps


def _run_session(ordered_questions, pre_responses, initial_state, bkt_params):
    """
    Run a BKT session given a pre-determined question order and responses.

    Returns
    -------
    mastered_counts : list of int — cumulative topics mastered after each
                      interaction (running maximum — once a topic crosses the
                      mastery threshold it is counted as mastered for the
                      remainder of the session, even if a later slip reduces
                      P(mastery) below the threshold).
    """
    state    = {k: float(v) for k, v in initial_state.items()}
    mastered = set()   # topics that have crossed the threshold
    counts   = []
    _fb      = {"p_learn": 0.25, "p_guess": 0.15, "p_slip": 0.12}

    for q in ordered_questions:
        topic  = q["topic"]
        resp   = pre_responses[q["id"]]
        bp     = bkt_params.get(topic, _fb)
        state[topic] = update_knowledge_state(
            state[topic], resp,
            bp["p_learn"], bp["p_guess"], bp["p_slip"],
        )
        # Accumulate mastered topics (never remove once added)
        for t, p in state.items():
            if p >= MASTERY_THRESHOLD:
                mastered.add(t)
        counts.append(len(mastered))

    return counts


def _adaptive_order(profile, questions, irt_dict, initial_state, bkt_params,
                    pre_responses, seed=SEED):
    """
    Return questions in adaptive order, updating BKT after each step to
    inform the next selection — but using pre_responses so outcomes are fixed.
    """
    _fb      = {"p_learn": 0.25, "p_guess": 0.15, "p_slip": 0.12}
    state    = {k: float(v) for k, v in initial_state.items()}
    answered = set()
    ordered  = []

    for _ in range(N_ITEMS):
        q = adaptive_next(questions, irt_dict, state, profile, answered)
        if q is None:
            break
        ordered.append(q)
        answered.add(q["id"])

        # Update state with the pre-generated response
        topic  = q["topic"]
        resp   = pre_responses[q["id"]]
        bp     = bkt_params.get(topic, _fb)
        state[topic] = update_knowledge_state(
            state[topic], resp,
            bp["p_learn"], bp["p_guess"], bp["p_slip"],
        )

    return ordered


def _static_order(profile, questions):
    """
    Return the questions in their natural bank order, filtered by audience.
    """
    return [q for q in questions if _is_eligible(q, profile)][:N_ITEMS]


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
    questions   = modules_data["questions"]
    profiles    = {p["id"]: p for p in profiles_data["simulation_profiles"]}
    bkt_params  = profiles_data["bkt_default_params"]

    irt_df  = pd.read_csv(irt_csv)
    irt_dict = {
        row["question_id"]: {
            "a_estimated": row["a_estimated"],
            "b_estimated": row["b_estimated"],
        }
        for _, row in irt_df.iterrows()
    }

    # ── Build figure ──────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=FIG_DOUBLE)

    for pid in PROFILE_ORDER:
        profile       = profiles[pid]
        color         = PROFILE_COLORS[pid]
        initial_state = profile["initial_knowledge_state"]

        pre_resps     = _pre_generate_responses(profile, questions, irt_dict)

        # Adaptive
        adap_qs       = _adaptive_order(profile, questions, irt_dict,
                                        initial_state, bkt_params, pre_resps)
        adap_counts   = _run_session(adap_qs, pre_resps, initial_state, bkt_params)

        # Static
        stat_qs       = _static_order(profile, questions)
        stat_counts   = _run_session(stat_qs, pre_resps, initial_state, bkt_params)

        x_adap = list(range(1, len(adap_counts) + 1))
        x_stat = list(range(1, len(stat_counts) + 1))

        ax.plot(x_adap, adap_counts,
                color=color, linestyle="-",  linewidth=2.0,
                label=f"{profile['display_name']} — Adaptive")
        ax.plot(x_stat, stat_counts,
                color=color, linestyle="--", linewidth=1.5, alpha=0.65,
                label=f"{profile['display_name']} — Static")

    # Reference line at full mastery
    ax.axhline(3, color=GRAY_DARK, linestyle=":", linewidth=0.8, alpha=0.6)
    ax.text(0.98, 3.06, "All 3 topics mastered",
            transform=ax.get_yaxis_transform(),
            ha="right", va="bottom", fontsize=6, color=GRAY_DARK)

    ax.set_xlim(0.5, 17.5)
    ax.set_ylim(-0.1, 3.4)
    ax.set_yticks([0, 1, 2, 3])
    ax.set_yticklabels(["0", "1", "2", "3"])
    ax.set_xlabel("Interaction Number", fontsize=8)
    ax.set_ylabel("Topics Mastered  (P ≥ 80%)", fontsize=8)
    ax.set_title(
        "Figure 6 — Adaptive vs. Static Knowledge Gain\n"
        "Cumulative topics mastered across 20 interactions  "
        "(solid = adaptive CEDAR-PKD,  dashed = static ordering)",
        fontsize=9, fontweight="bold",
    )

    # ── Custom legend: profile colours + line-style legend ────────────────
    profile_patches = [
        mpatches.Patch(color=PROFILE_COLORS[pid],
                       label=profiles[pid]["display_name"])
        for pid in PROFILE_ORDER
    ]
    style_lines = [
        mlines.Line2D([], [], color="black", linestyle="-",  linewidth=1.5,
                      label="Adaptive (CEDAR-PKD)"),
        mlines.Line2D([], [], color="black", linestyle="--", linewidth=1.2,
                      alpha=0.7, label="Static (fixed order)"),
    ]

    leg1 = ax.legend(
        handles=profile_patches,
        loc="upper left", fontsize=7, framealpha=0.9,
        title="Learner Profile", title_fontsize=7,
    )
    ax.add_artist(leg1)
    ax.legend(
        handles=style_lines,
        loc="lower right", fontsize=7, framealpha=0.9,
    )

    plt.tight_layout()
    save_figure(fig, "fig6_adaptive_vs_static")
    plt.close(fig)
    print("Figure 6 complete.")


if __name__ == "__main__":
    main()
