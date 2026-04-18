# CEDAR-PKD Prototype

**Core Education Development Adaptive Resource for PKD**

A prototype Adaptive Learning Engine (ALE) for ADPKD education, built to generate
preliminary data figures for the NIH R01 resubmission (1R01DK149254).

---

## Context

| Field | Detail |
|---|---|
| **Disease** | Autosomal Dominant Polycystic Kidney Disease (ADPKD) |
| **Grant** | NIH R01DK149254-01 resubmission (impact score 38, percentile 23) |
| **PI** | Brittany N. Lasseigne, University of Alabama at Birmingham |
| **Co-Is** | Michal Mrug MD, Matthew Might PhD |
| **Also informs** | DOD PRMRP resubmission (PR250279) |

Reviewers flagged CEDAR-PKD (Aim 3) as having insufficient specification of
the adaptive learning engine — no IRT model named, no proof-of-concept, no
learning objectives taxonomy, no demographic variables. This prototype directly
addresses each of those critiques with working code and grant-ready figures.

---

## Session Progress

| Session | Status | What was built |
|---|---|---|
| 1 | ✅ Complete | Project scaffold, shared figure style, content layer (3 modules, 20 questions, user profiles) |
| 2 | ✅ Complete | 2PL IRT engine, simulation pipeline, Figures 2–4 |
| 3 | ✅ Complete | BKT engine, content recommender, Figures 5–7 |
| 4 | ✅ Complete | Streamlit app (Figure 1), CEDAR vs. BIRCH schematic (Figure 8), compile_all.py |
| Post-session | ✅ Complete | Figure 6 redesigned as 2×2 small multiples; Figure 8 overlap fixed; Figure 1 readability improved; full 13-page technical report (`generate_report.py`); mock AI misconception feedback panel in Figure 1; LLM integration vision page added to report |

---

## Figure Map

| Figure | Description | Reviewer Concern Addressed | Status |
|---|---|---|---|
| **Fig 1** | Prototype screenshots — patient view (unanswered) + physician view (wrong answer → AI misconception feedback panel) | No ALE proof-of-concept; UI too dense for patients | ✅ Done |
| **Fig 2** | IRT Item Characteristic Curves (2PL model, 3 panels) | IRT model unspecified (NIH Critique 1) | ✅ Done |
| **Fig 3** | Item parameter table (a, b, Bloom's, demographic tags) | No item calibration detail; no demographic variables | ✅ Done |
| **Fig 4** | Learning objectives taxonomy (Bloom's + IRT difficulty) | No learning objectives taxonomy defined | ✅ Done |
| **Fig 5** | Simulated learner trajectories (4 user profiles, BKT) | Adaptive logic not validated | ✅ Done |
| **Fig 6** | Adaptive vs. static knowledge gain — 2×2 small multiples | Why individualised learning improves outcomes | ✅ Done |
| **Fig 7** | Demographically-tailored learning paths | No demographic variables; sex/gender tailoring missing | ✅ Done |
| **Fig 8** | CEDAR vs. BIRCH differentiation schematic | CEDAR necessity questioned (DOD Reviewer B) | ✅ Done |

---

## Repository Structure

```
cedar-pkd_prototype/
├── content/
│   ├── modules.json          ← 3 modules, 20 questions (full metadata)
│   └── user_profiles.json    ← 4 simulation profiles + 3 demographic profiles + BKT defaults
│
├── models/
│   ├── irt.py                ← 2PL IRT: p_correct(), estimate_parameters(), get_icc_data()
│   ├── bkt.py                ← Bayesian Knowledge Tracing
│   └── recommender.py        ← Content recommender (audience filter + demographic boosts)
│
├── simulation/
│   └── simulate.py           ← Response matrix generation + IRT estimation; saves to outputs/
│
├── figures/
│   ├── style.py              ← Shared apply_cedar_style() + save_figure() + color palettes
│   ├── fig1_app_screenshot.py ← Prototype UI mock (patient view + physician wrong-answer + AI panel)
│   ├── fig2_icc.py           ← ICC curves (3-panel, one per module)
│   ├── fig3_item_params.py   ← Item parameter table
│   ├── fig4_taxonomy.py      ← Learning objectives taxonomy
│   ├── fig5_trajectories.py  ← BKT mastery trajectories (4 profiles × 3 topics)
│   ├── fig6_adaptive_vs_static.py  ← Adaptive vs. static — 2×2 small multiples
│   ├── fig7_demographic_paths.py   ← Demographically-tailored learning paths
│   ├── fig8_cedar_birch.py         ← CEDAR vs. BIRCH differentiation schematic
│   └── compile_all.py              ← Regenerate all 8 figures in one command
│
├── app/
│   └── cedar_app.py          ← Streamlit ALE app (streamlit run app/cedar_app.py)
│
├── generate_report.py        ← 13-page technical report PDF (see Technical Report section)
├── outputs/                  ← Generated figures + report (gitignored — regenerate locally)
├── requirements.txt
└── README.md
```

---

## Setup

```bash
# Standard environments
pip install -r requirements.txt

# macOS with Homebrew-managed Python (python3 --version >= 3.12)
pip install -r requirements.txt --break-system-packages
```

**Requirements:** numpy, scipy, pandas, matplotlib, seaborn, scikit-learn, streamlit

---

## Reproducing the Figures

### Run the simulation (generates IRT params + response matrix)
```bash
python simulation/simulate.py
```

### Generate all 8 figures at once
```bash
python figures/compile_all.py           # runs simulation + all figures (~15 s)
python figures/compile_all.py --fast    # skip simulation, use cached IRT params
```

### Generate individual figures
```bash
python figures/fig1_app_screenshot.py
python figures/fig2_icc.py
python figures/fig3_item_params.py
python figures/fig4_taxonomy.py
python figures/fig5_trajectories.py
python figures/fig6_adaptive_vs_static.py
python figures/fig7_demographic_paths.py
python figures/fig8_cedar_birch.py
```

### Run the Streamlit app prototype
```bash
streamlit run app/cedar_app.py
```

All figures are saved to `outputs/` as both 300 DPI PNG and PDF.
The `outputs/` directory is gitignored — run the scripts above to regenerate locally.

---

## Technical Report

`generate_report.py` produces a 13-page letter-size PDF at `outputs/cedar_pkd_report.pdf`
that documents the full prototype for grant reviewers.

```bash
python generate_report.py
```

### Report page map

| Page | Title | Contents |
|---|---|---|
| 1 | Title | Grant context, reviewer critiques overview |
| 2 | System Architecture | CEDAR-PKD component diagram |
| 3 | Session 1 — Content Layer | 3 modules, 20 questions, Bloom's taxonomy, demographic tags, simulation profiles |
| 4 | Session 2 — IRT Model + Fig 2 | 2PL IRT rationale, ICC curves |
| 5 | Figures 3 & 4 | Item parameter table + learning objectives taxonomy (full page width) |
| 6 | Session 3 — BKT + Recommender | BKT update rule, recommender scoring formula |
| 7 | Figure 5 | Simulated BKT mastery trajectories |
| 8 | Figure 6 | Adaptive vs. static comparison (2×2 small multiples) |
| 9 | Figure 7 | Demographically-tailored learning paths |
| 10 | Session 4 — Prototype UI (Fig 1) | App mock-up with AI misconception feedback panel |
| 11 | Figure 8 | CEDAR vs. BIRCH schematic with purple shared-driver box explained |
| 12 | Summary | Reviewer critique → response mapping table + conclusion |
| 13 | Production Vision — LLM Integration | Architecture table, 4 planned LLM features with testable hypotheses |

---

## Content Layer Summary

**3 modules, 20 questions** — all with full metadata:

| Module | Title | Questions | Audience |
|---|---|---|---|
| 1.2 | An Overview of ADPKD | 6 | Both |
| 1.3 | ADPKD Genetics | 6 | Both |
| 2.3 | Genetic Testing for ADPKD | 8 | Both |

**Question metadata fields:** `blooms_level` (remember/understand/apply),
`difficulty_prior` → 2PL `b` parameter, `audience` (patient/physician/both),
`demographic_tags` (sex_specific, disease_stage_relevant, family_planning_relevant),
`distractor_misconceptions` (misconception label per wrong-answer option).

**4 simulation profiles** (for Figures 5 & 6): newly_diagnosed_patient (θ=−1.5),
experienced_patient (θ=0.0), primary_care_physician (θ=1.0), nephrologist (θ=1.8).

**3 demographic profiles** (for Figure 7): female patient / early stage / family planning,
male patient / advanced stage (CKD 4), treating physician.

---

## IRT Model Details

The 2-Parameter Logistic (2PL) model was selected over:
- **1PL (Rasch):** too restrictive — items span 3 Bloom's levels and 3 topic areas,
  so varying discrimination is expected and meaningful
- **3PL:** guessing parameter unnecessary for informed clinical learners answering
  ADPKD-specific 4-option questions; can be added if pilot data supports it

Parameters estimated by item-level MLE (L-BFGS-B with bounds) from 100 simulated
users. All 20 items converged. Estimated `b` tracks difficulty priors closely.

---

## BKT Model Details

Bayesian Knowledge Tracing (Corbett & Anderson, 1994) maintains a per-topic
probabilistic mastery estimate updated after every quiz interaction:

| Parameter | Description | Default |
|---|---|---|
| `p_learn` | P(transition: unlearned → learned) per opportunity | 0.25–0.30 per topic |
| `p_guess` | P(correct \| unlearned) | 0.15–0.20 per topic |
| `p_slip`  | P(incorrect \| learned) | 0.10–0.12 per topic |
| `p_known` | P(mastery) — updated dynamically | from `initial_knowledge_state` |

**Update rule** (two-step Bayesian):
1. Posterior given response: `P(known|obs) = P(known)·L(obs|known) / P(obs)`
2. Learning transition: `P(known_new) = P(known|obs) + (1 − P(known|obs)) · p_learn`

**Mastery threshold:** P(mastery) ≥ 0.80

BKT was chosen over raw accuracy tracking because it accounts for guessing and
slipping, giving a principled stopping criterion and per-topic gap quantification
that drives the content recommender.

---

## Content Recommender Details

Items are scored at each adaptive step:

```
score_i = (1 − P(mastery_topic_i)) × a_i
          + 0.30  [if sex_specific and learner sex is specified]
          + 0.40  [if family_planning_relevant and learner.family_planning = True]
          + 0.30  [if disease_stage_relevant includes learner's CKD stage]
```

Audience filtering ensures patient-only items are never shown to physicians and
vice versa. Items already answered are excluded. The highest-scoring eligible
item is selected at each step (greedy one-step look-ahead).

**Figure 6 note:** "Topics mastered" uses a running maximum — once a topic
crosses P(mastery) = 0.80 it is counted as mastered for the rest of the session,
even if a subsequent slip lowers the BKT estimate. This is the clinically
appropriate interpretation: mastery gained is not "unlearned" in one session.

---

## CEDAR-PKD vs. BIRCH-PKD (Figure 8)

DOD Reviewer B asked why CEDAR is needed given BIRCH. They are complementary
tools that address different types of knowledge gaps:

| | BIRCH-PKD | CEDAR-PKD |
|---|---|---|
| **Mode** | Reactive — user-initiated | Proactive — system-initiated |
| **Mechanism** | Evidence-based Q&A chatbot | Adaptive Learning Engine |
| **Gap type** | Known unknowns | Unknown unknowns |
| **Trigger** | User asks a specific question | BKT detects a mastery gap |
| **Output** | Single focused answer | Personalised curriculum path |

Neither tool alone is sufficient: BIRCH answers questions users know to ask;
CEDAR surfaces and fills gaps users did not know they had.

The **purple box** at the top of Figure 8 represents the shared problem driver —
ADPKD knowledge gaps in patients and clinicians — from which both tools are
responses. Arrows flow downward from it to both BIRCH and CEDAR.

---

## LLM Integration Vision (Production CEDAR-PKD)

The prototype implements the psychometric core (IRT + BKT + demographic recommender).
Production CEDAR-PKD adds LLMs as a complementary layer — not replacing the
adaptive engine but handling tasks LLMs are uniquely suited for:

| Layer | Technology | Status |
|---|---|---|
| Sequencing | IRT + BKT | ✅ Implemented |
| Explanation | LLM (GPT-4o / Claude) — misconception-targeted feedback | 🟣 Prototyped (Fig 1) |
| BIRCH handoff | BKT threshold → BIRCH trigger | 🔵 Designed |
| Item scaling | LLM generation → IRT validation pipeline | 🟠 Proposed |

**Four planned features** (see report page 13 for full detail + testable hypotheses):
1. **Misconception-Targeted Explanations** — wrong answer triggers LLM feedback conditioned on the item's `distractor_misconceptions` tag, learner role, and CKD stage *(prototyped in Fig 1)*
2. **BKT-Triggered BIRCH Handoff** — persistent gap (P < 0.50 for 3 interactions) surfaces a contextual BIRCH prompt
3. **LLM Item Generation + IRT Validation Pipeline** — scales bank from 20 → 200+ calibrated items
4. **Personalized Session Debrief Narrative** — LLM-written end-of-session summary tailored to role and mastery state

**Core argument:** IRT + BKT decide *what to teach next and when to stop*;
LLMs decide *how to explain it* for this specific learner in this specific context.
Pure LLM tutors lack a principled stopping criterion, measurable item properties,
and auditable mastery tracking. This combination provides all three.
