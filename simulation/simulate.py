"""
simulation/simulate.py
Core simulation pipeline for CEDAR-PKD prototype.

Generates a synthetic response matrix from the four user profiles defined in
content/user_profiles.json, then estimates 2PL IRT parameters from those
responses and saves everything to outputs/ for use by figure scripts.

Usage
-----
    python simulation/simulate.py          # run from project root
    from simulation.simulate import run_simulation  # import in figure scripts
"""

import json
import os
import sys

import numpy as np
import pandas as pd

# ── path setup so this script runs from any working directory ──────────────
_HERE    = os.path.dirname(os.path.abspath(__file__))
_ROOT    = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from models.irt import p_correct, estimate_parameters, prior_to_b, b_to_tier


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_content():
    """
    Load modules.json and user_profiles.json from content/.

    Returns
    -------
    modules_data  : dict parsed from modules.json
    profiles_data : dict parsed from user_profiles.json
    """
    content_dir = os.path.join(_ROOT, "content")
    with open(os.path.join(content_dir, "modules.json"))       as f:
        modules_data  = json.load(f)
    with open(os.path.join(content_dir, "user_profiles.json")) as f:
        profiles_data = json.load(f)
    return modules_data, profiles_data


# ---------------------------------------------------------------------------
# Response matrix simulation
# ---------------------------------------------------------------------------

def simulate_responses(modules_data, profiles_data, seed=42):
    """
    Generate a binary response matrix (n_users × n_items) by sampling from
    the 2PL model using each user profile's theta distribution and item
    difficulty priors.

    Parameters
    ----------
    modules_data  : dict from modules.json
    profiles_data : dict from user_profiles.json
    seed          : int — random seed for reproducibility

    Returns
    -------
    response_matrix : np.ndarray (n_users, n_items), dtype int (0/1)
    theta_array     : np.ndarray (n_users,)          — sampled ability values
    question_ids    : list of str                    — item identifiers
    profile_labels  : list of str                    — profile id per user
    b_priors        : np.ndarray (n_items,)          — prior b from difficulty_prior
    a_priors        : np.ndarray (n_items,)          — prior a (all 1.0)
    """
    rng       = np.random.default_rng(seed)
    questions = modules_data["questions"]
    profiles  = profiles_data["simulation_profiles"]

    # Convert difficulty priors to b-parameter scale
    b_priors = np.array([prior_to_b(q["difficulty_prior"]) for q in questions])
    a_priors = np.ones(len(questions))   # default discrimination = 1.0

    all_thetas   = []
    all_responses = []
    all_labels   = []

    for profile in profiles:
        thetas = rng.normal(
            profile["theta"],
            profile["theta_sd"],
            profile["n_simulated_users"],
        )
        for theta in thetas:
            probs     = p_correct(theta, a_priors, b_priors)
            responses = rng.binomial(1, probs).astype(int)
            all_thetas.append(theta)
            all_responses.append(responses)
            all_labels.append(profile["id"])

    response_matrix = np.array(all_responses)   # (100, 20)
    theta_array     = np.array(all_thetas)       # (100,)
    question_ids    = [q["id"] for q in questions]

    return response_matrix, theta_array, question_ids, all_labels, b_priors, a_priors


# ---------------------------------------------------------------------------
# Main simulation runner — estimates IRT params and saves all outputs
# ---------------------------------------------------------------------------

def run_simulation(seed=42, verbose=True):
    """
    Full simulation pipeline:
      1. Load content
      2. Generate response matrix
      3. Estimate 2PL IRT parameters (a, b) per item
      4. Save response_matrix.csv, theta_array.csv, irt_params.csv to outputs/
      5. Return a data dict consumed by figure scripts

    Parameters
    ----------
    seed    : int  — random seed
    verbose : bool — print progress

    Returns
    -------
    data : dict with keys:
        modules_data, profiles_data,
        response_matrix, theta_array, question_ids, profile_labels,
        b_priors, a_priors,
        a_estimated, b_estimated,
        irt_params_df   (pandas DataFrame)
    """
    out_dir = os.path.join(_ROOT, "outputs")
    os.makedirs(out_dir, exist_ok=True)

    if verbose:
        print("Loading content...")
    modules_data, profiles_data = load_content()
    questions = modules_data["questions"]

    if verbose:
        print("Simulating response matrix (100 users × 20 items)...")
    response_matrix, theta_array, question_ids, profile_labels, b_priors, a_priors = \
        simulate_responses(modules_data, profiles_data, seed=seed)

    if verbose:
        print("Estimating 2PL IRT parameters (MLE per item)...")
    a_estimated, b_estimated, converged = estimate_parameters(
        response_matrix, theta_array
    )

    n_converged = sum(converged)
    if verbose:
        print(f"  Converged: {n_converged}/{len(converged)} items")

    # ── Build IRT params DataFrame ─────────────────────────────────────────
    records = []
    for j, q in enumerate(questions):
        records.append({
            "question_id":    q["id"],
            "module_id":      q["module_id"],
            "topic":          q["topic"],
            "audience":       q["audience"],
            "blooms_level":   q["blooms_level"],
            "difficulty_prior": q["difficulty_prior"],
            "b_prior":        b_priors[j],
            "a_prior":        a_priors[j],
            "a_estimated":    round(a_estimated[j], 3),
            "b_estimated":    round(b_estimated[j], 3),
            "difficulty_tier": b_to_tier(b_estimated[j]),
            "sex_specific":   q["demographic_tags"]["sex_specific"],
            "family_planning": q["demographic_tags"]["family_planning_relevant"],
            "converged":      converged[j],
        })

    irt_params_df = pd.DataFrame(records)

    # ── Save to outputs/ ───────────────────────────────────────────────────
    irt_params_df.to_csv(os.path.join(out_dir, "irt_params.csv"), index=False)

    # Save response matrix with labels
    rm_df = pd.DataFrame(
        response_matrix,
        columns=question_ids,
    )
    rm_df.insert(0, "profile",     profile_labels)
    rm_df.insert(1, "theta_true",  theta_array)
    rm_df.to_csv(os.path.join(out_dir, "response_matrix.csv"), index=False)

    if verbose:
        print(f"  Saved irt_params.csv and response_matrix.csv to outputs/")
        print("\nIRT parameter summary:")
        print(irt_params_df[["question_id", "b_prior", "b_estimated",
                              "a_estimated", "difficulty_tier"]].to_string(index=False))

    return {
        "modules_data":     modules_data,
        "profiles_data":    profiles_data,
        "response_matrix":  response_matrix,
        "theta_array":      theta_array,
        "question_ids":     question_ids,
        "profile_labels":   profile_labels,
        "b_priors":         b_priors,
        "a_priors":         a_priors,
        "a_estimated":      a_estimated,
        "b_estimated":      b_estimated,
        "irt_params_df":    irt_params_df,
    }


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    data = run_simulation(verbose=True)
    print("\nDone. Files written to outputs/")
