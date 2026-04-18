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

| Session | Steps | Status | What was built |
|---|---|---|---|
| 1 | 0–2 | ✅ Complete | Project scaffold, shared figure style, content layer (3 modules, 20 questions, user profiles) |
| 2 | 3–6 | ✅ Complete | 2PL IRT engine, simulation pipeline, Figures 2–4 |
| 3 | 7–11 | 🔲 Pending | BKT engine, content recommender, Figures 5–7 |
| 4 | 12–15 | 🔲 Pending | Streamlit app (Figure 1), CEDAR vs. BIRCH schematic (Figure 8), compile_all.py |

---

## Figure Map

| Figure | Description | Reviewer Concern Addressed | Status |
|---|---|---|---|
| **Fig 1** | Prototype screenshots — patient vs. physician views | No ALE proof-of-concept; UI too dense for patients | 🔲 Session 4 |
| **Fig 2** | IRT Item Characteristic Curves (2PL model, 3 panels) | IRT model unspecified (NIH Critique 1) | ✅ Done |
| **Fig 3** | Item parameter table (a, b, Bloom's, demographic tags) | No item calibration detail; no demographic variables | ✅ Done |
| **Fig 4** | Learning objectives taxonomy (Bloom's + IRT difficulty) | No learning objectives taxonomy defined | ✅ Done |
| **Fig 5** | Simulated learner trajectories (4 user profiles, BKT) | Adaptive logic not validated | 🔲 Session 3 |
| **Fig 6** | Adaptive vs. static knowledge gain comparison | Why individualized learning improves outcomes | 🔲 Session 3 |
| **Fig 7** | Demographically-tailored learning paths | No demographic variables; sex/gender tailoring missing | 🔲 Session 3 |
| **Fig 8** | CEDAR vs. BIRCH differentiation schematic | CEDAR necessity questioned (DOD Reviewer B) | 🔲 Session 4 |

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
│   ├── bkt.py                ← Bayesian Knowledge Tracing  [Session 3]
│   └── recommender.py        ← Content recommender         [Session 3]
│
├── simulation/
│   └── simulate.py           ← Response matrix generation + IRT estimation; saves to outputs/
│
├── figures/
│   ├── style.py              ← Shared apply_cedar_style() + save_figure() + color palettes
│   ├── fig2_icc.py           ← ICC curves (3-panel, one per module)
│   ├── fig3_item_params.py   ← Item parameter table
│   ├── fig4_taxonomy.py      ← Learning objectives taxonomy
│   ├── fig5_trajectories.py  ← [Session 3]
│   ├── fig6_adaptive_vs_static.py  ← [Session 3]
│   ├── fig7_demographic_paths.py   ← [Session 3]
│   ├── fig8_cedar_birch.py         ← [Session 4]
│   └── compile_all.py              ← [Session 4]
│
├── app/
│   └── cedar_app.py          ← Streamlit ALE app           [Session 4]
│
├── outputs/                  ← Generated figures (gitignored — regenerate locally)
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

### Generate individual figures
```bash
python figures/fig2_icc.py
python figures/fig3_item_params.py
python figures/fig4_taxonomy.py
```

### Generate all figures at once (available after Session 4)
```bash
python figures/compile_all.py
```

All figures are saved to `outputs/` as both 300 DPI PNG and PDF.
The `outputs/` directory is gitignored — run the scripts above to regenerate locally.

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
