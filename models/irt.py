"""
models/irt.py
Two-Parameter Logistic (2PL) Item Response Theory model for CEDAR-PKD.

The 2PL model defines the probability that a user with latent ability theta
answers a question correctly, given that question's discrimination (a) and
difficulty (b) parameters:

    P(correct | theta, a, b) = 1 / (1 + exp(-a * (theta - b)))

Parameters
----------
theta : float or array — latent ability of the learner (standardized, mean 0)
a     : float — discrimination: how steeply the ICC rises at b;
                typical range [0.5, 2.5]; higher = better differentiator
b     : float — difficulty: the theta value at which P(correct) = 0.5;
                negative = easy (below-average ability sufficient),
                positive = hard (above-average ability needed)

Why 2PL over 1PL (Rasch) or 3PL?
    1PL fixes a=1 for all items — too restrictive when items differ in how
    well they discriminate learners (our items span 3 Bloom's levels and
    3 topic areas, so varying discrimination is expected).
    3PL adds a guessing parameter (c) useful for multiple-choice where
    random guessing is likely. With 4-option items and informed learners we
    use 2PL; 3PL can be added in future work if pilot data supports it.
"""

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit   # numerically stable logistic sigmoid


# ---------------------------------------------------------------------------
# Core 2PL probability function
# ---------------------------------------------------------------------------

def p_correct(theta, a, b):
    """
    2PL probability of a correct response.

    Parameters
    ----------
    theta : float or np.ndarray  — learner ability
    a     : float or np.ndarray  — item discrimination
    b     : float or np.ndarray  — item difficulty

    Returns
    -------
    float or np.ndarray in (0, 1)
    """
    return expit(a * (theta - b))


# ---------------------------------------------------------------------------
# Item parameter estimation (marginal MLE per item, known theta)
# ---------------------------------------------------------------------------

def _neg_log_likelihood_item(params, theta_array, responses):
    """
    Negative log-likelihood for a single item given known ability estimates.
    Used internally by estimate_parameters.
    """
    a, b = params
    if a <= 0:
        return 1e10    # enforce positive discrimination
    p = p_correct(theta_array, a, b)
    p = np.clip(p, 1e-9, 1.0 - 1e-9)   # avoid log(0)
    ll = responses * np.log(p) + (1.0 - responses) * np.log(1.0 - p)
    return -np.sum(ll)


def estimate_parameters(response_matrix, theta_array):
    """
    Estimate 2PL item parameters (a, b) for every item via item-level MLE,
    treating theta_array as known (fixed-effects approach).

    This is appropriate here because theta values are either sampled from
    known simulation distributions or estimated from an initial ability
    assessment. For production use, full marginal MLE (EM algorithm) would
    be preferred.

    Parameters
    ----------
    response_matrix : np.ndarray, shape (n_users, n_items) — binary (0/1)
    theta_array     : np.ndarray, shape (n_users,)         — ability values

    Returns
    -------
    a_params : np.ndarray, shape (n_items,) — discrimination estimates
    b_params : np.ndarray, shape (n_items,) — difficulty estimates
    converged: list of bool, length n_items — optimizer convergence flags
    """
    n_items = response_matrix.shape[1]
    a_params   = np.zeros(n_items)
    b_params   = np.zeros(n_items)
    converged  = []

    for j in range(n_items):
        responses = response_matrix[:, j].astype(float)

        result = minimize(
            _neg_log_likelihood_item,
            x0=[1.0, 0.0],          # start at a=1, b=0 (neutral item)
            args=(theta_array, responses),
            method="L-BFGS-B",
            bounds=[(0.10, 5.00),   # a: positive, practically bounded
                    (-4.00, 4.00)], # b: IRT convention
            options={"ftol": 1e-8, "maxiter": 2000},
        )

        a_params[j]  = result.x[0]
        b_params[j]  = result.x[1]
        converged.append(result.success)

    return a_params, b_params, converged


# ---------------------------------------------------------------------------
# ICC curve data for plotting
# ---------------------------------------------------------------------------

def get_icc_data(a, b, theta_range=(-3.5, 3.5), n_points=300):
    """
    Return (theta_vals, p_vals) arrays for plotting an Item Characteristic
    Curve.

    Parameters
    ----------
    a           : float — discrimination
    b           : float — difficulty
    theta_range : tuple — (min, max) for the ability axis
    n_points    : int   — number of points along the curve

    Returns
    -------
    theta_vals : np.ndarray, shape (n_points,)
    p_vals     : np.ndarray, shape (n_points,)
    """
    theta_vals = np.linspace(theta_range[0], theta_range[1], n_points)
    p_vals     = p_correct(theta_vals, a, b)
    return theta_vals, p_vals


# ---------------------------------------------------------------------------
# Difficulty prior → b parameter conversion
# ---------------------------------------------------------------------------

def prior_to_b(difficulty_prior):
    """
    Convert a hand-assigned difficulty prior (0–1 float from modules.json)
    to the b parameter scale used in 2PL IRT.

    Mapping:
        difficulty_prior = 0.2 (easy)   → b ≈ −1.2
        difficulty_prior = 0.5 (medium) → b =  0.0
        difficulty_prior = 0.8 (hard)   → b ≈ +1.2

    Formula: b = (difficulty_prior − 0.5) × 4
    """
    return (difficulty_prior - 0.5) * 4.0


def b_to_tier(b):
    """
    Convert an estimated b parameter to a human-readable difficulty tier.
        b < −0.5  → 'Easy'
        −0.5 ≤ b ≤ 0.5 → 'Medium'
        b >  0.5  → 'Hard'
    """
    if b < -0.5:
        return "Easy"
    elif b <= 0.5:
        return "Medium"
    else:
        return "Hard"
