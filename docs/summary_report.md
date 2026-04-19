# Project Summary — CEDAR-PKD Prototype

**Last updated:** 2026-04-19
**Maintainer:** Brittany N. Lasseigne, University of Alabama at Birmingham

---

## Overview

CEDAR-PKD (Core Education Development Adaptive Resource for PKD) is a prototype
Adaptive Learning Engine (ALE) for Autosomal Dominant Polycystic Kidney Disease
(ADPKD) education. The prototype was built to generate preliminary data and
grant-ready figures for the NIH R01 resubmission (1R01DK149254) and also informs
the DOD PRMRP resubmission (PR250279).

The system delivers personalised ADPKD education to patients and clinicians by
adaptively sequencing quiz items based on learner ability (IRT) and real-time
mastery tracking (BKT), with demographic-aware content prioritisation.

---

## Rationale

NIH reviewers flagged CEDAR-PKD (Aim 3) for insufficient specification:

| Reviewer Critique | Response |
|---|---|
| No IRT model named or specified | 2PL IRT implemented with MLE estimation; ICC plots generated (Fig 2, 3) |
| No proof-of-concept or working prototype | Functional Streamlit ALE; all 8 figures from working code (Fig 1) |
| No learning objectives taxonomy defined | Bloom's taxonomy × IRT difficulty matrix across 20 calibrated items (Fig 4) |
| No demographic variables in adaptive engine | Sex-specific, family-planning, CKD-stage boosts in recommender (Fig 7) |
| Individualised learning benefit not justified | Controlled adaptive vs. static comparison, same responses, ordering only differs (Fig 6) |
| Why CEDAR when BIRCH-PKD exists? (DOD Reviewer B) | Complementary tools: BIRCH = known unknowns (reactive); CEDAR = unknown unknowns (proactive) (Fig 8) |

---

## Methods & Pipeline

### Content Layer (`content/`)
- **3 modules**, 20 questions with full metadata per item:
  - `blooms_level`: remember / understand / apply
  - `difficulty_prior` → 2PL IRT `b` parameter
  - `audience`: patient / physician / both
  - `demographic_tags`: sex_specific, disease_stage_relevant, family_planning_relevant
  - `distractor_misconceptions`: misconception label per wrong-answer option
- **4 simulation profiles** (θ = −1.5, 0.0, 1.0, 1.8)
- **3 demographic profiles** for Figure 7

### IRT Engine (`models/irt.py`)
- 2-Parameter Logistic model: P(correct | θ, a, b) = sigmoid(a·(θ−b))
- Parameters estimated by item-level MLE (L-BFGS-B) from 100 simulated users
- All 20 items converged; estimated `b` tracks difficulty priors

### BKT Engine (`models/bkt.py`)
- Bayesian Knowledge Tracing (Corbett & Anderson, 1994)
- Per-topic P(mastery) updated after every interaction
- Mastery threshold: P(mastery) ≥ 0.80; running maximum (mastery not reversed by slip)

### Content Recommender (`models/recommender.py`)
- Greedy one-step look-ahead
- Score: `(1 − P(mastery_topic)) × discrimination + demographic_boosts`
- Audience filtering; already-answered items excluded

### Simulation (`simulation/simulate.py`)
- Generates 100-learner response matrix via IRT-simulated responses
- Runs IRT MLE estimation; saves `outputs/irt_params.csv`

### Figures (`figures/`)
- 8 grant-ready figures; all generated from working Python scripts
- Shared style system: `figures/style.py`
- `figures/compile_all.py` regenerates all 8 in ~15 seconds

### Streamlit App (`app/cedar_app.py`)
- Interactive ALE proof-of-concept
- Role selection (patient / clinician), BKT-driven question delivery, live mastery sidebar

### Technical Report (`generate_report.py`)
- 13-page letter-size PDF; fully reproducible from a single command
- Covers all methods, all figures, reviewer critique mapping, and LLM vision

---

## Current Status

| Component | Status |
|---|---|
| Content layer (modules, questions, profiles) | ✅ Complete |
| IRT engine (2PL, MLE estimation) | ✅ Complete |
| BKT engine | ✅ Complete |
| Content recommender (demographic boosts) | ✅ Complete |
| Simulation pipeline | ✅ Complete |
| All 8 grant figures | ✅ Complete |
| Streamlit prototype app | ✅ Complete |
| 13-page technical report | ✅ Complete |
| AI misconception feedback panel (Fig 1 prototype) | ✅ Prototyped |
| LLM integration vision (report page 13) | ✅ Documented |
| README.md | ✅ Current |
| docs/decision_log.md | ✅ Created 2026-04-19 |
| docs/summary_report.md | ✅ Created 2026-04-19 |
| GitHub (blasseigne/cedar-pkd_prototype) | ✅ Fully pushed |

---

## Key Results & Figures

| Figure | File | Key Finding |
|---|---|---|
| Fig 1 | `figures/fig1_app_screenshot.py` | Role-differentiated UI; physician wrong-answer state shows mock AI misconception feedback panel (purple) — prototype of LLM explanation layer |
| Fig 2 | `figures/fig2_icc.py` | ICC curves for all 20 items; discrimination varies meaningfully across Bloom's levels, justifying 2PL over 1PL |
| Fig 3 | `figures/fig3_item_params.py` | Item parameter table: estimated a, b, Bloom's level, audience, demographic tags for all 20 items |
| Fig 4 | `figures/fig4_taxonomy.py` | Learning objectives taxonomy: Bloom's level × IRT difficulty scatter; items span the full intended range |
| Fig 5 | `figures/fig5_trajectories.py` | BKT mastery trajectories for 4 profiles; adaptive sequencing tracks mastery appropriately — stalls at hard items, accelerates on well-targeted ones |
| Fig 6 | `figures/fig6_adaptive_vs_static.py` | Adaptive outpaces static by 3–8 interactions for experienced/physician/nephrologist profiles; newly diagnosed patient crossover is delayed (mechanistically explained in panel annotation and report) |
| Fig 7 | `figures/fig7_demographic_paths.py` | Demographic boosts (sex, CKD stage, family planning) alter item selection order visibly; same θ, different paths |
| Fig 8 | `figures/fig8_cedar_birch.py` | BIRCH (reactive, known unknowns) vs. CEDAR (proactive, unknown unknowns); purple shared-driver box = ADPKD knowledge gap problem motivating both tools |

---

## Decisions & Design Choices

See `docs/decision_log.md` for full entries. Key decisions:

- **2PL IRT** chosen over 1PL (too restrictive) and 3PL (guessing parameter unwarranted)
- **BKT** chosen over raw accuracy — provides principled stopping criterion and per-topic gap quantification
- **Greedy one-step recommender** — sufficient for 20-item bank; multi-step look-ahead over-engineered
- **Mastery threshold 0.80** — standard ITS threshold; clinically appropriate
- **Figure 6 as 2×2 small multiples** — shows full trajectory, not cherry-picked milestones; honest about delayed crossover for newly diagnosed patient
- **Figure 8 title via fig.suptitle** — prevents overlap with purple box; in-axes text caused ~0.05 unit overlap hiding box text
- **AI panel in Figure 1** — physician wrong-answer state chosen to prototype LLM misconception feedback layer
- **Report as matplotlib PDF** — single-command reproducibility, no new dependencies
- **CAPTURE not adopted** — prototype scope; no HPC, no external data, no containers

---

## Known Issues & Limitations

| Issue | Severity | Notes |
|---|---|---|
| 20-question bank is prototype scale | Expected | Production requires 200+ IRT-calibrated items; LLM generation pipeline designed for this |
| IRT calibration uses simulated responses | Expected | Real pilot data needed for final parameter estimates; simulation demonstrates feasibility |
| BKT parameters are defaults, not empirically estimated | Expected | `p_learn`, `p_guess`, `p_slip` from literature priors; pilot data will enable fitting |
| AI explanation panel is mocked, not live LLM | Expected | Demonstrates design and UI; production requires API integration |
| Streamlit app not deployed | Low priority | Local prototype; deployment (Streamlit Cloud / HPC) planned for pilot phase |
| Newly diagnosed patient never reaches full mastery in Fig 6 session | By design | θ = −1.5 with few correct answers; realistic for a newly diagnosed patient; explained in figure annotation |

---

## Future Plans

### Near-term (grant revision)
- Incorporate all 8 figures and the technical report into the NIH R01 resubmission narrative
- Use LLM vision page (report p. 13) to address Aim 3 specification in the proposal text

### Pilot study (if funded)
1. **Expand item bank**: LLM-generated items → SME review → IRT calibration → 200+ items
2. **BKT parameter fitting**: estimate p_learn, p_guess, p_slip from pilot response data
3. **Live LLM integration**: connect AI explanation panel to GPT-4o or Claude API
4. **BKT-triggered BIRCH handoff**: implement threshold-based handoff when P(mastery) < 0.50 for 3 consecutive interactions on same topic
5. **Personalized session debrief**: LLM-generated end-of-session narrative
6. **Deploy Streamlit app**: Streamlit Cloud or UAB HPC for pilot participants
7. **Formal usability testing**: patient and clinician cohorts; SUS + learning outcome measures

### Open questions
- Optimal mastery threshold (0.80) — should be validated against learning outcomes in pilot
- Whether to adopt CAPTURE for the pilot pipeline (HPC execution will likely necessitate it)
- 3PL guessing parameter — revisit if pilot data shows floor effects in patient cohort

---

## Dependencies & Requirements

```
Python >= 3.10
numpy
scipy
pandas
matplotlib
seaborn
scikit-learn
streamlit
```

Install: `pip install -r requirements.txt`

macOS (Homebrew Python ≥ 3.12): `pip install -r requirements.txt --break-system-packages`

No containers, no HPC, no external data downloads required for the prototype.
All outputs are regenerable locally in ~15 seconds from `python figures/compile_all.py`
and ~5 seconds from `python generate_report.py`.
