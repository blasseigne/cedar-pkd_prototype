"""
app/cedar_app.py
CEDAR-PKD Streamlit Prototype — Adaptive Learning Engine

A working ALE prototype for ADPKD education that demonstrates:
  • Role-differentiated content (patient vs. physician)
  • BKT-driven mastery tracking per topic
  • Adaptive item selection via the content recommender
  • Real-time mastery progress display

Usage (run from project root)
------------------------------
    streamlit run app/cedar_app.py

Session flow
------------
    setup → quiz (question → feedback → next question ...) → complete

Session state keys
------------------
    phase              : 'setup' | 'quiz' | 'complete'
    role               : 'patient' | 'physician'
    knowledge_state    : {topic: P(mastery)}
    bkt_params         : {topic: {p_learn, p_guess, p_slip}}
    answered_ids       : set of question ids already shown
    current_question   : dict | None
    feedback           : {correct, selected_key, correct_key, explanation} | None
    history            : list of per-interaction dicts
    item_count         : int
    correct_count      : int
"""

import os
import sys

import numpy as np
import pandas as pd
import streamlit as st

# ── Path setup (allows running from project root or app/) ─────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from models.bkt          import update_knowledge_state, topics_mastered
from models.recommender  import adaptive_next
from simulation.simulate import load_content, run_simulation

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MASTERY_THRESHOLD    = 0.80
MAX_ITEMS_PER_SESSION = 15

TOPIC_DISPLAY = {
    "kidney_basics":    "Kidney Basics",
    "adpkd_genetics":   "ADPKD Genetics",
    "adpkd_diagnosis":  "Genetic Testing",
}

TOPIC_EMOJI = {
    "kidney_basics":    "🫘",
    "adpkd_genetics":   "🧬",
    "adpkd_diagnosis":  "🔬",
}

# ---------------------------------------------------------------------------
# Data loading — cached so models load only once per server process
# ---------------------------------------------------------------------------

@st.cache_resource
def load_app_data():
    """Load content + IRT params; run simulation if outputs don't exist."""
    modules_data, profiles_data = load_content()

    irt_csv = os.path.join(_ROOT, "outputs", "irt_params.csv")
    if not os.path.exists(irt_csv):
        run_simulation(verbose=False)

    irt_df   = pd.read_csv(irt_csv)
    irt_dict = {
        row["question_id"]: {
            "a_estimated": float(row["a_estimated"]),
            "b_estimated": float(row["b_estimated"]),
        }
        for _, row in irt_df.iterrows()
    }

    return modules_data, profiles_data, irt_dict


# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

def _init_state():
    defaults = {
        "phase":            "setup",
        "role":             None,
        "knowledge_state":  None,
        "bkt_params":       None,
        "answered_ids":     set(),
        "current_question": None,
        "feedback":         None,
        "history":          [],
        "item_count":       0,
        "correct_count":    0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ---------------------------------------------------------------------------
# Shared sidebar — mastery progress
# ---------------------------------------------------------------------------

def _sidebar():
    with st.sidebar:
        st.markdown("## 📊 Your Progress")
        st.caption(f"Mastery threshold: {int(MASTERY_THRESHOLD * 100)}%")
        st.divider()

        for topic in ["kidney_basics", "adpkd_genetics", "adpkd_diagnosis"]:
            p   = st.session_state.knowledge_state.get(topic, 0.0)
            pct = int(p * 100)
            done = p >= MASTERY_THRESHOLD
            color = "#27AE60" if done else "#2980B9"
            badge = "  ✓" if done else ""

            st.markdown(
                f"""
                <div style="margin-bottom:10px;">
                  <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                    <span style="font-weight:600;font-size:0.85em;">
                      {TOPIC_EMOJI[topic]} {TOPIC_DISPLAY[topic]}{badge}
                    </span>
                    <span style="font-size:0.82em;color:#666;">{pct}%</span>
                  </div>
                  <div style="background:#E0E0E0;border-radius:5px;height:9px;">
                    <div style="background:{color};width:{pct}%;border-radius:5px;
                                height:9px;"></div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()
        n_mastered = topics_mastered(
            st.session_state.knowledge_state, MASTERY_THRESHOLD
        )
        col_a, col_b = st.columns(2)
        col_a.metric("Mastered", f"{n_mastered}/3")
        col_b.metric("Questions", st.session_state.item_count)

        if st.session_state.item_count > 0:
            acc = st.session_state.correct_count / st.session_state.item_count
            st.metric("Accuracy", f"{acc:.0%}")

        st.divider()
        if st.button("↩ Start Over", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


# ---------------------------------------------------------------------------
# Screen: Setup (role selection)
# ---------------------------------------------------------------------------

def _setup_screen():
    st.markdown(
        """
        <div style="text-align:center; padding:30px 0 10px 0;">
          <h1 style="color:#2C3E50;font-size:2.2em;">🧬 CEDAR-PKD</h1>
          <p style="font-size:1.1em;color:#555;margin-top:-8px;">
            Core Education Development Adaptive Resource for PKD
          </p>
          <p style="color:#777;max-width:580px;margin:12px auto 0 auto;
                    font-size:0.95em;line-height:1.55;">
            An adaptive learning engine that personalises ADPKD education to your
            role, background knowledge, and individual learning needs — filling
            the knowledge gaps you didn't know you had.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown("### Who are you?")
    st.caption(
        "Your role determines which questions and level of clinical detail you receive."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div style="border:1.5px solid #AED6F1;border-radius:10px;
                        padding:16px;margin-bottom:8px;background:#F7FBFF;">
              <h4 style="margin:0 0 6px 0;">👤 Patient or Caregiver</h4>
              <ul style="font-size:0.88em;color:#555;margin:0;padding-left:18px;">
                <li>Plain-language explanations</li>
                <li>Focus on daily life &amp; decisions</li>
                <li>Inheritance, symptoms, treatment options</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "Start as Patient / Caregiver",
            use_container_width=True,
            type="primary",
        ):
            _start_session("patient")

    with col2:
        st.markdown(
            """
            <div style="border:1.5px solid #A9DFBF;border-radius:10px;
                        padding:16px;margin-bottom:8px;background:#F7FFF9;">
              <h4 style="margin:0 0 6px 0;">🩺 Healthcare Provider</h4>
              <ul style="font-size:0.88em;color:#555;margin:0;padding-left:18px;">
                <li>Clinical terminology &amp; guidelines</li>
                <li>Genetics, testing, variant interpretation</li>
                <li>Management &amp; cascade testing workflows</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "Start as Healthcare Provider",
            use_container_width=True,
            type="primary",
        ):
            _start_session("physician")


def _start_session(role):
    _, profiles_data, _ = load_app_data()
    st.session_state.role            = role
    st.session_state.knowledge_state = {
        "kidney_basics":    0.20,
        "adpkd_genetics":   0.10,
        "adpkd_diagnosis":  0.10,
    }
    st.session_state.bkt_params      = profiles_data["bkt_default_params"]
    st.session_state.answered_ids    = set()
    st.session_state.current_question = None
    st.session_state.feedback        = None
    st.session_state.history         = []
    st.session_state.item_count      = 0
    st.session_state.correct_count   = 0
    st.session_state.phase           = "quiz"
    st.rerun()


# ---------------------------------------------------------------------------
# Screen: Quiz
# ---------------------------------------------------------------------------

def _quiz_screen():
    modules_data, _, irt_dict = load_app_data()
    questions = modules_data["questions"]

    # Completion check
    n_mastered = topics_mastered(
        st.session_state.knowledge_state, MASTERY_THRESHOLD
    )
    if n_mastered == 3 or st.session_state.item_count >= MAX_ITEMS_PER_SESSION:
        st.session_state.phase = "complete"
        st.rerun()
        return

    _sidebar()

    # Show feedback from previous answer
    if st.session_state.feedback is not None:
        _show_feedback(questions, irt_dict)
        return

    # Fetch next question if needed
    if st.session_state.current_question is None:
        user_profile = {
            "role":           st.session_state.role,
            "sex":            "not_specified",
            "disease_stage":  None,
            "family_planning": False,
        }
        q = adaptive_next(
            questions, irt_dict,
            st.session_state.knowledge_state,
            user_profile,
            st.session_state.answered_ids,
        )
        if q is None:
            st.session_state.phase = "complete"
            st.rerun()
            return
        st.session_state.current_question = q

    _show_question()


def _show_question():
    q   = st.session_state.current_question
    num = st.session_state.item_count + 1
    role_label = "Patient Mode" if st.session_state.role == "patient" else "Clinician Mode"

    # Question header
    st.markdown(
        f"<span style='color:#888;font-size:0.82em;'>"
        f"Question {num} &nbsp;·&nbsp; {role_label} &nbsp;·&nbsp; "
        f"{TOPIC_EMOJI[q['topic']]} {TOPIC_DISPLAY[q['topic']]}"
        f"</span>",
        unsafe_allow_html=True,
    )
    st.markdown(f"### {q['text']}")
    st.divider()

    for key in ["A", "B", "C", "D"]:
        if key in q["options"]:
            if st.button(
                f"**{key}.**  {q['options'][key]}",
                key=f"ans_{q['id']}_{key}",
                use_container_width=True,
            ):
                _record_response(key)
                st.rerun()


def _record_response(selected_key):
    q       = st.session_state.current_question
    correct = selected_key == q["correct_answer"]

    # BKT update
    topic = q["topic"]
    bp    = st.session_state.bkt_params.get(
        topic, {"p_learn": 0.25, "p_guess": 0.15, "p_slip": 0.12}
    )
    st.session_state.knowledge_state[topic] = update_knowledge_state(
        st.session_state.knowledge_state[topic],
        int(correct),
        bp["p_learn"], bp["p_guess"], bp["p_slip"],
    )

    st.session_state.answered_ids.add(q["id"])
    st.session_state.item_count += 1
    if correct:
        st.session_state.correct_count += 1

    st.session_state.history.append({
        "question_id":     q["id"],
        "topic":           topic,
        "correct":         correct,
        "selected":        selected_key,
        "knowledge_state": dict(st.session_state.knowledge_state),
    })

    st.session_state.feedback = {
        "correct":      correct,
        "selected_key": selected_key,
        "correct_key":  q["correct_answer"],
        "explanation":  q["explanation"],
        "options":      q["options"],
    }


def _show_feedback(questions, irt_dict):
    fb = st.session_state.feedback
    q  = st.session_state.current_question

    if fb["correct"]:
        st.success(
            f"✅ **Correct!** &nbsp; {fb['options'][fb['correct_key']]}"
        )
    else:
        st.error(
            f"❌ **Incorrect.** &nbsp; You selected: {fb['options'][fb['selected_key']]}"
        )
        st.info(
            f"**Correct answer:** {fb['correct_key']}. {fb['options'][fb['correct_key']]}"
        )

    with st.expander("📖 Explanation", expanded=True):
        st.markdown(fb["explanation"])

    st.divider()

    if st.button("Next Question →", use_container_width=True, type="primary"):
        user_profile = {
            "role":           st.session_state.role,
            "sex":            "not_specified",
            "disease_stage":  None,
            "family_planning": False,
        }
        next_q = adaptive_next(
            questions, irt_dict,
            st.session_state.knowledge_state,
            user_profile,
            st.session_state.answered_ids,
        )
        st.session_state.current_question = next_q
        st.session_state.feedback         = None
        st.rerun()


# ---------------------------------------------------------------------------
# Screen: Complete
# ---------------------------------------------------------------------------

def _complete_screen():
    _sidebar()

    st.markdown(
        "<h2 style='text-align:center;'>🎉 Session Complete!</h2>",
        unsafe_allow_html=True,
    )

    ks         = st.session_state.knowledge_state
    n_mastered = topics_mastered(ks, MASTERY_THRESHOLD)
    acc        = (
        st.session_state.correct_count / st.session_state.item_count
        if st.session_state.item_count > 0
        else 0.0
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Topics Mastered", f"{n_mastered} / 3")
    col2.metric("Questions Answered", st.session_state.item_count)
    col3.metric("Session Accuracy", f"{acc:.0%}")

    st.divider()
    st.markdown("### Mastery Summary")

    for topic in ["kidney_basics", "adpkd_genetics", "adpkd_diagnosis"]:
        p      = ks.get(topic, 0.0)
        status = "✅ Mastered" if p >= MASTERY_THRESHOLD else "📈 In Progress"
        st.markdown(
            f"**{TOPIC_EMOJI[topic]} {TOPIC_DISPLAY[topic]}** — "
            f"{p:.0%} &nbsp; {status}"
        )

    # Gap-based recommendations
    gaps = [t for t, p in ks.items() if p < MASTERY_THRESHOLD]
    if gaps:
        st.divider()
        st.markdown("### 📚 Recommended for Next Session")
        for t in gaps:
            st.markdown(
                f"- **{TOPIC_DISPLAY[t]}** ({ks[t]:.0%} mastery — "
                f"more practice recommended)"
            )
    else:
        st.success(
            "🏆 Excellent! You've reached mastery across all ADPKD topic areas."
        )

    st.divider()
    if st.button("Start a New Session", use_container_width=True, type="primary"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    st.set_page_config(
        page_title  = "CEDAR-PKD",
        page_icon   = "🧬",
        layout      = "wide",
        initial_sidebar_state = "auto",
    )

    # Lightweight CSS polish
    st.markdown(
        """
        <style>
        .stButton > button { border-radius: 8px; }
        .stMetric [data-testid="stMetricValue"] { font-size: 1.4em; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    _init_state()

    if st.session_state.phase == "setup":
        _setup_screen()
    elif st.session_state.phase == "quiz":
        _quiz_screen()
    elif st.session_state.phase == "complete":
        _complete_screen()


if __name__ == "__main__":
    main()
