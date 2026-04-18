"""
models/recommender.py
Content recommender for CEDAR-PKD adaptive learning sessions.

The recommender selects the next question that maximises expected learning
value for a specific learner, combining:

  1. BKT-informed topic gaps  — questions on topics where P(mastery) is low
     contribute more to learning gain.
  2. IRT discrimination       — highly discriminating items carry more
     information regardless of topic.
  3. Demographic relevance    — items tagged as sex-specific, family-planning-
     relevant, or disease-stage-specific receive additive boosts when the
     learner profile matches those tags.
  4. Audience filtering       — items intended for a specific audience
     (patient-only or physician-only) are never shown to the other role.

Scoring formula for eligible item i:

    score_i = (1 − P(mastery_topic_i)) × a_i
              + boost_sex_specific      (if applicable)
              + boost_family_planning   (if applicable)
              + boost_disease_stage     (if applicable)

At each step the highest-scoring unanswered eligible item is selected.

References
----------
  Doignon & Falmagne (1999) — Knowledge Spaces.
  Corbett & Anderson (1994) — BKT original paper.
  van der Linden & Hambleton (1997) — CAT / adaptive testing foundations.
"""

import numpy as np

# ---------------------------------------------------------------------------
# Demographic boost weights (additive to base score)
# ---------------------------------------------------------------------------
BOOST_SEX_SPECIFIC    = 0.30   # item has sex-specific clinical content
BOOST_FAMILY_PLANNING = 0.40   # item is relevant to reproductive planning
BOOST_DISEASE_STAGE   = 0.30   # item matches learner's current CKD stage


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _is_eligible(question, user_profile):
    """
    Return True if the question is appropriate for this user's role.

    audience == 'both'      — eligible for any role
    audience == 'patient'   — only shown to patients
    audience == 'physician' — only shown to physicians
    """
    role     = user_profile.get("role", "patient")
    audience = question.get("audience", "both")
    if audience == "both":
        return True
    return audience == role


def _score_item(question, a_estimated, knowledge_state, user_profile):
    """
    Compute the recommender score for one eligible item.

    Parameters
    ----------
    question        : dict from modules.json
    a_estimated     : float — IRT discrimination for this item
    knowledge_state : dict {topic: P(mastery)}
    user_profile    : dict — must have 'role'; optionally 'sex',
                      'disease_stage', 'family_planning'

    Returns
    -------
    float — score (higher = higher learning value for this learner right now)
    """
    topic     = question["topic"]
    p_mastery = knowledge_state.get(topic, 0.50)
    base      = (1.0 - p_mastery) * float(a_estimated)

    demo_tags = question.get("demographic_tags", {})
    boost     = 0.0

    # Sex-specific boost — only when learner has a specified biological sex
    if demo_tags.get("sex_specific", False):
        sex = user_profile.get("sex", "not_specified")
        if sex in ("female", "male"):
            boost += BOOST_SEX_SPECIFIC

    # Family-planning boost
    if demo_tags.get("family_planning_relevant", False):
        if user_profile.get("family_planning", False):
            boost += BOOST_FAMILY_PLANNING

    # Disease-stage relevance boost
    stage_list = demo_tags.get("disease_stage_relevant", [])
    if stage_list:
        user_stage = user_profile.get("disease_stage", None)
        if user_stage is not None and int(user_stage) in [int(s) for s in stage_list]:
            boost += BOOST_DISEASE_STAGE

    return base + boost


# ---------------------------------------------------------------------------
# Core adaptive selection functions
# ---------------------------------------------------------------------------

def adaptive_next(questions, irt_params, knowledge_state, user_profile, answered_ids):
    """
    Select the single best next question for the given learner state.

    Parameters
    ----------
    questions       : list of question dicts from modules.json
    irt_params      : dict {question_id: {'a_estimated': float, 'b_estimated': float}}
    knowledge_state : dict {topic: P(mastery)}
    user_profile    : dict — must contain 'role'; optionally demographic fields
    answered_ids    : set/list of question ids already presented this session

    Returns
    -------
    dict — the selected question dict, or None if no eligible items remain
    """
    answered_set = set(answered_ids)
    best_q       = None
    best_score   = -np.inf

    for q in questions:
        if q["id"] in answered_set:
            continue
        if not _is_eligible(q, user_profile):
            continue
        a  = irt_params.get(q["id"], {}).get("a_estimated", 1.0)
        sc = _score_item(q, a, knowledge_state, user_profile)
        if sc > best_score:
            best_score = sc
            best_q     = q

    return best_q


def generate_learning_path(
    questions,
    irt_params,
    knowledge_state,
    user_profile,
    bkt_params,
    n_items=10,
    rng=None,
):
    """
    Generate an adaptive learning path, simulating IRT responses and BKT
    updates at each step.

    The path is built greedily: at each step the highest-scoring eligible
    unanswered item is selected, a response is simulated from the 2PL model
    using user_profile['theta'], and the BKT knowledge state is updated.

    Parameters
    ----------
    questions       : list of question dicts from modules.json
    irt_params      : dict {question_id: {a_estimated, b_estimated}}
    knowledge_state : dict {topic: P(mastery)} — initial state (not mutated)
    user_profile    : dict — must contain 'role' and 'theta'; optionally
                      demographic fields (sex, disease_stage, family_planning)
    bkt_params      : dict {topic: {p_learn, p_guess, p_slip}}
    n_items         : int — maximum number of items in the path
    rng             : numpy Generator (or None → np.random.default_rng(42))

    Returns
    -------
    path   : list of question dicts in recommended order (length ≤ n_items)
    states : list of knowledge_state dicts AFTER each question (same length)
    responses : list of int (0/1), one per step
    """
    from models.irt import p_correct
    from models.bkt import update_knowledge_state

    if rng is None:
        rng = np.random.default_rng(42)

    state    = {k: float(v) for k, v in knowledge_state.items()}
    answered = set()
    path     = []
    states   = []
    resps    = []
    theta    = float(user_profile.get("theta", 0.0))

    _fallback_bkt = {"p_learn": 0.25, "p_guess": 0.15, "p_slip": 0.12}

    for _ in range(n_items):
        q = adaptive_next(questions, irt_params, state, user_profile, answered)
        if q is None:
            break

        # Simulate response via 2PL IRT
        item   = irt_params.get(q["id"], {})
        a_est  = float(item.get("a_estimated", 1.0))
        b_est  = float(item.get("b_estimated", 0.0))
        prob   = float(p_correct(theta, a_est, b_est))
        resp   = int(rng.binomial(1, prob))

        # BKT update
        topic       = q["topic"]
        bp          = bkt_params.get(topic, _fallback_bkt)
        state[topic] = update_knowledge_state(
            state[topic], resp,
            bp["p_learn"], bp["p_guess"], bp["p_slip"],
        )

        path.append(q)
        answered.add(q["id"])
        states.append(dict(state))
        resps.append(resp)

    return path, states, resps
