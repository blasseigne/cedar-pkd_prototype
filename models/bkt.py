"""
models/bkt.py
Bayesian Knowledge Tracing (BKT) for CEDAR-PKD.

BKT models the probability that a learner has mastered a knowledge component
(topic) at each point in a learning session. It updates after every quiz
interaction using Bayes' theorem, then applies a learning transition.

Four parameters per knowledge component (topic):
    p_learn  — P(transition from unlearned → learned) after an opportunity
    p_guess  — P(correct | unlearned)   — learner guesses correctly
    p_slip   — P(incorrect | learned)   — learner slips despite knowing
    p_known  — P(mastery) at the current timestep (updated dynamically)

Standard BKT update rule (Corbett & Anderson, 1994):

    Step 1 — Bayesian update given observed response:
        If correct:
            P(known | correct) = P(known)·(1−p_slip)
                                 ─────────────────────────────────────────
                                 P(known)·(1−p_slip) + (1−P(known))·p_guess

        If incorrect:
            P(known | incorrect) = P(known)·p_slip
                                   ──────────────────────────────────────────
                                   P(known)·p_slip + (1−P(known))·(1−p_guess)

    Step 2 — Learning transition:
        P(known_new) = P(known|response) + (1 − P(known|response)) · p_learn

Why BKT over simpler methods?
    Unlike item-level scoring (correct/incorrect counts), BKT maintains a
    probabilistic estimate of latent mastery that accounts for guessing and
    slipping. This is essential for CEDAR-PKD because:
    1. ADPKD questions have varying difficulty — a wrong answer on a hard
       question should update mastery differently than on an easy one.
    2. BKT gives a principled stopping criterion (P(mastery) > threshold).
    3. Extensions to Bayesian knowledge tracing (e.g., time-dependent BKT,
       deep knowledge tracing) can be incorporated in future iterations.

Default parameters (sourced from published ALE literature) are stored in
content/user_profiles.json under 'bkt_default_params'.
"""

import numpy as np


# ---------------------------------------------------------------------------
# Core update function
# ---------------------------------------------------------------------------

def update_knowledge_state(p_known, correct, p_learn, p_guess, p_slip):
    """
    Apply one BKT update step for a single knowledge component.

    Parameters
    ----------
    p_known  : float — current P(mastery) for this topic, in [0, 1]
    correct  : int or bool — 1 if response was correct, 0 if incorrect
    p_learn  : float — learning rate (probability of learning per opportunity)
    p_guess  : float — guessing probability
    p_slip   : float — slipping probability

    Returns
    -------
    float — updated P(mastery) after this interaction
    """
    if correct:
        p_known_given_response = (
            p_known * (1.0 - p_slip)
        ) / (
            p_known * (1.0 - p_slip) + (1.0 - p_known) * p_guess
        )
    else:
        p_known_given_response = (
            p_known * p_slip
        ) / (
            p_known * p_slip + (1.0 - p_known) * (1.0 - p_guess)
        )

    # Learning transition
    p_known_new = (
        p_known_given_response
        + (1.0 - p_known_given_response) * p_learn
    )

    return float(np.clip(p_known_new, 0.0, 1.0))


# ---------------------------------------------------------------------------
# Session runner
# ---------------------------------------------------------------------------

def run_bkt_session(question_sequence, responses, initial_state, bkt_params):
    """
    Run BKT over an ordered sequence of quiz interactions.

    Parameters
    ----------
    question_sequence : list of question dicts (each has a 'topic' key)
    responses         : list of int (1=correct, 0=incorrect), same length
    initial_state     : dict — {topic: P(mastery)} at session start
    bkt_params        : dict — {topic: {p_learn, p_guess, p_slip}}

    Returns
    -------
    history : list of dicts, length = len(question_sequence)
              Each entry is {topic: P(mastery)} after that interaction.
    """
    state   = {k: float(v) for k, v in initial_state.items()}
    history = []

    for q, r in zip(question_sequence, responses):
        topic  = q["topic"]
        params = bkt_params[topic]

        state[topic] = update_knowledge_state(
            state[topic],
            int(r),
            params["p_learn"],
            params["p_guess"],
            params["p_slip"],
        )
        history.append(dict(state))

    return history


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------

def topics_mastered(knowledge_state, threshold=0.80):
    """
    Return the number of topics where P(mastery) >= threshold.

    Parameters
    ----------
    knowledge_state : dict — {topic: P(mastery)}
    threshold       : float — mastery cutoff (default 0.80)

    Returns
    -------
    int — count of mastered topics
    """
    return sum(1 for p in knowledge_state.values() if p >= threshold)


def mastery_vector(history, threshold=0.80):
    """
    Return a list of cumulative topics-mastered counts across a session history.

    Parameters
    ----------
    history   : list of {topic: P(mastery)} dicts (from run_bkt_session)
    threshold : float

    Returns
    -------
    list of int, length = len(history)
    """
    return [topics_mastered(state, threshold) for state in history]
