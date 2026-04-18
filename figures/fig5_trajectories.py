"""
figures/fig5_trajectories.py
Figure 5 — Simulated BKT Mastery Trajectories (2 × 2 panel)

One panel per simulation profile.  Each panel shows P(mastery) for all three
ADPKD topic areas as a function of adaptive interaction number, together with
the mastery-threshold reference line.

Addresses reviewer concern: "Adaptive logic not validated — no proof that the
engine actually tracks knowledge gain across diverse learner types."

Generation
----------
    python figures/fig5_trajectories.py       # run from project root
"""

import json
import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── path setup ────────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from figures.style import (
    apply_cedar_style, save_figure,
    PROFILE_COLORS, TOPIC_COLORS, THRESHOLD_COLOR,
    GRAY_MED, FIG_PANEL22,
)
from models.bkt        import update_knowledge_state
from models.recommender import adaptive_next, _is_eligible
from models.irt         import p_correct
from simulation.simulate import load_content, run_simulation

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MASTERY_THRESHOLD = 0.80
N_ITEMS           = 20       # interactions per session
SEED              = 42

TOPIC_ORDER       = ["kidney_basics", "adpkd_genetics", "adpkd_diagnosis"]
TOPIC_LABELS      = {
    "kidney_basics":    "Kidney Basics",
    "adpkd_genetics":   "ADPKD Genetics",
    "adpkd_diagnosis":  "Genetic Testing",
}
TOPIC_LINE_STYLES = {
    "kidney_basics":   "-",
    "adpkd_genetics":  "--",
    "adpkd_diagnosis": ":",
}
TOPIC_MARKERS = {
    "kidney_basics":   "o",
    "adpkd_genetics":  "s",
    "adpkd_diagnosis": "^",
}

PROFILE_ORDER = [
    "newly_diagnosed_patient",
    "experienced_patient",
    "primary_care_physician",
    "nephrologist",
]

# ---------------------------------------------------------------------------
# Simulation helper
# ---------------------------------------------------------------------------

def simulate_adaptive_session(profile, questions, irt_dict, bkt_params, seed=SEED):
    """
    Run one adaptive BKT session for a simulation profile.

    Returns
    -------
    history : list of {topic: P(mastery)} dicts, one per step (length ≤ N_ITEMS)
    """
    rng      = np.random.default_rng(seed)
    state    = {k: float(v) for k, v in profile["initial_knowledge_state"].items()}
    answered = set()
    history  = []
    theta    = float(profile["theta"])

    _fallback = {"p_learn": 0.25, "p_guess": 0.15, "p_slip": 0.12}

    for _ in range(N_ITEMS):
        q = adaptive_next(questions, irt_dict, state, profile, answered)
        if q is None:
            break

        item  = irt_dict.get(q["id"], {})
        a_est = float(item.get("a_estimated", 1.0))
        b_est = float(item.get("b_estimated", 0.0))
        prob  = float(p_correct(theta, a_est, b_est))
        resp  = int(rng.binomial(1, prob))

        topic        = q["topic"]
        bp           = bkt_params.get(topic, _fallback)
        state[topic] = update_knowledge_state(
            state[topic], resp,
            bp["p_learn"], bp["p_guess"], bp["p_slip"],
        )

        answered.add(q["id"])
        history.append(dict(state))

    return history


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

    irt_df      = pd.read_csv(irt_csv)
    irt_dict    = {
        row["question_id"]: {
            "a_estimated": row["a_estimated"],
            "b_estimated": row["b_estimated"],
        }
        for _, row in irt_df.iterrows()
    }

    # ── Build figure ──────────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=FIG_PANEL22, sharex=False, sharey=True)
    axes_flat = axes.flatten()

    for idx, pid in enumerate(PROFILE_ORDER):
        ax      = axes_flat[idx]
        profile = profiles[pid]
        history = simulate_adaptive_session(profile, questions, irt_dict, bkt_params, seed=SEED)

        n_steps = len(history)
        x       = list(range(1, n_steps + 1))

        for topic in TOPIC_ORDER:
            y = [state[topic] for state in history]
            ax.plot(
                x, y,
                color     = TOPIC_COLORS[topic],
                linestyle = TOPIC_LINE_STYLES[topic],
                marker    = TOPIC_MARKERS[topic],
                markersize= 4,
                linewidth = 1.8,
                markevery = 4,
                label     = TOPIC_LABELS[topic],
            )

        # Mastery threshold
        ax.axhline(
            MASTERY_THRESHOLD,
            color     = THRESHOLD_COLOR,
            linestyle = "-.",
            linewidth = 1.0,
            alpha     = 0.8,
            label     = f"Mastery threshold ({MASTERY_THRESHOLD:.0%})",
        )

        ax.set_title(profile["display_name"], fontsize=9, fontweight="bold",
                     color=PROFILE_COLORS[pid], pad=4)
        ax.set_ylim(-0.02, 1.02)
        ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(["0%", "20%", "40%", "60%", "80%", "100%"], fontsize=7)
        ax.set_xlim(0.5, n_steps + 0.5)
        ax.set_xlabel("Adaptive Interaction #", fontsize=8)
        if idx % 2 == 0:
            ax.set_ylabel("P(Mastery)", fontsize=8)

        # Initial state annotation
        init = profile["initial_knowledge_state"]
        init_avg = np.mean(list(init.values()))
        ax.annotate(
            f"Start: {init_avg:.0%}",
            xy=(1, list(history[0].values())[0]),
            xytext=(3, init_avg + 0.10),
            fontsize=6, color="#666666",
            arrowprops=dict(arrowstyle="->", color="#AAAAAA", lw=0.8),
        )

    # ── Shared legend ─────────────────────────────────────────────────────
    # Build from first axis handles
    handles, labels = axes_flat[0].get_legend_handles_labels()
    fig.legend(
        handles, labels,
        loc            = "lower center",
        ncol           = 4,
        fontsize       = 7,
        frameon        = True,
        bbox_to_anchor = (0.5, -0.03),
        framealpha     = 0.9,
    )

    fig.suptitle(
        "Figure 5 — Simulated Learner BKT Mastery Trajectories\n"
        "Adaptive CEDAR-PKD sessions (20 interactions) across four learner profiles",
        fontsize=9, fontweight="bold", y=1.01,
    )

    plt.tight_layout(rect=[0, 0.06, 1, 1])
    save_figure(fig, "fig5_trajectories")
    plt.close(fig)
    print("Figure 5 complete.")


if __name__ == "__main__":
    main()
