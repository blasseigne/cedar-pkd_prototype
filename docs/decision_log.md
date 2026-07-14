# Decision Log — CEDAR-PKD Prototype

Substantive design and implementation decisions made across all project sessions.
Each entry records what was decided, why, what was rejected, and which files are affected.

---

## [2026-04-17] Choose 2PL IRT over 1PL (Rasch) and 3PL

**Decision:** Use the 2-Parameter Logistic (2PL) IRT model for item calibration.

**Rationale:** Items span 3 Bloom's taxonomy levels (remember / understand / apply) and 3 topic areas. Varying discrimination across items is expected and scientifically meaningful — the 2PL captures this. The 1PL (Rasch) forces equal discrimination, which is too restrictive given item heterogeneity. The 3PL adds a guessing parameter, which is unnecessary for informed clinical learners answering domain-specific 4-option questions.

**Alternatives considered:**
- *1PL (Rasch):* Rejected — too restrictive; discrimination differences are real and meaningful across Bloom's levels.
- *3PL:* Rejected — guessing parameter not warranted for this population; adds complexity without interpretive gain. Can be revisited if pilot data shows systematic floor effects.

**Scripts impacted:** `models/irt.py`, `simulation/simulate.py`, `figures/fig2_icc.py`, `figures/fig3_item_params.py`

**Status:** Active

---

## [2026-04-17] Choose Bayesian Knowledge Tracing (BKT) over raw accuracy tracking

**Decision:** Use BKT (Corbett & Anderson, 1994) for per-topic mastery estimation rather than tracking raw accuracy or a rolling average.

**Rationale:** BKT accounts for guessing (P(correct | unlearned)) and slipping (P(incorrect | learned)), giving a principled probabilistic mastery estimate. This provides: (1) a defensible stopping criterion (P(mastery) ≥ 0.80), (2) per-topic gap quantification that drives the recommender, and (3) a well-established psychometric precedent for grant review.

**Alternatives considered:**
- *Raw accuracy (rolling mean):* Rejected — no principled stopping criterion; doesn't distinguish guessing from knowing.
- *Item Response Theory alone:* Rejected — IRT estimates static item difficulty; BKT tracks dynamic learner state over time. Both are used together.

**Scripts impacted:** `models/bkt.py`, `models/recommender.py`, `figures/fig5_trajectories.py`, `app/cedar_app.py`

**Status:** Active

---

## [2026-04-17] Greedy one-step look-ahead for content recommender

**Decision:** Use greedy one-step look-ahead for item selection: score all eligible items at each step and select the highest scorer. No multi-step planning.

**Rationale:** Scoring function `(1 − P(mastery_topic)) × discrimination + demographic_boosts` captures the key desiderata (target weak topics, prefer high-discrimination items, boost demographically relevant content). Multi-step look-ahead would add substantial complexity with marginal gain given the short session length (15–20 items).

**Alternatives considered:**
- *Random selection within eligible items:* Rejected — no personalisation signal.
- *Multi-step tree search / RL policy:* Rejected — over-engineered for a prototype with 20 items and 3 topics; would complicate interpretability for grant review.

**Scripts impacted:** `models/recommender.py`, `figures/fig6_adaptive_vs_static.py`, `figures/fig7_demographic_paths.py`

**Status:** Active

---

## [2026-04-17] Mastery threshold set at P(mastery) ≥ 0.80

**Decision:** A topic is considered mastered when BKT P(mastery) reaches 0.80 or above.

**Rationale:** 0.80 is a standard mastery threshold in ITS and CAT literature; it represents confident mastery while acknowledging BKT's inherent uncertainty. Once crossed, mastery is tracked as a running maximum — a topic is not "unmastered" by a subsequent slip, which is clinically appropriate.

**Alternatives considered:**
- *0.70:* Too permissive — learners may still have meaningful gaps.
- *0.90:* Too stringent for a 15–20 item session; few learners would reach mastery within session length.

**Scripts impacted:** `models/bkt.py`, `models/recommender.py`, `figures/fig5_trajectories.py`, `figures/fig6_adaptive_vs_static.py`

**Status:** Active

---

## [2026-04-17] Content layer: 3 modules, 20 questions with full metadata

**Decision:** Implement 3 ADPKD modules (Overview, Genetics, Genetic Testing) with 20 questions, each carrying: `blooms_level`, `difficulty_prior`, `audience`, `demographic_tags`, and `distractor_misconceptions`.

**Rationale:** 20 questions is sufficient for a proof-of-concept prototype demonstrating all engine components. The metadata fields directly address every reviewer critique: Bloom's taxonomy answers "no learning objectives taxonomy"; demographic tags answer "no demographic variables"; distractor misconceptions enable the AI feedback layer.

**Alternatives considered:**
- *Fewer questions (10):* Insufficient to demonstrate IRT calibration and adaptive advantage across profiles.
- *More questions (50+):* Appropriate for a pilot study, not a prototype; manual authoring at scale is not the prototype's goal.

**Scripts impacted:** `content/modules.json`, `content/user_profiles.json`

**Status:** Active

---

## [2026-04-17] Four simulation profiles spanning the learner ability range

**Decision:** Define 4 simulation profiles: newly_diagnosed_patient (θ=−1.5), experienced_patient (θ=0.0), primary_care_physician (θ=1.0), nephrologist (θ=1.8).

**Rationale:** The four profiles span the realistic ability range from low (newly diagnosed patient with no prior knowledge) to high (nephrologist specialist). This demonstrates that the adaptive engine performs appropriately across the full spectrum and that personalization is meaningful — not just theoretical.

**Alternatives considered:**
- *Two profiles (patient / physician):* Too coarse; doesn't distinguish within-role ability variation.
- *Continuous θ sampling:* Appropriate for a full trial; over-complex for grant figures.

**Scripts impacted:** `content/user_profiles.json`, `simulation/simulate.py`, `figures/fig5_trajectories.py`, `figures/fig6_adaptive_vs_static.py`

**Status:** Active

---

## [2026-04-18] Figure 6 layout: 2×2 small multiples over single-panel or milestone bar chart

**Decision:** Redesign Figure 6 as a 2×2 small-multiples layout (one panel per learner profile) showing full cumulative mastery trajectories, with solid = adaptive, dashed = static, shaded area = adaptive advantage gap.

**Rationale:** Three design options were evaluated:
- *Option A (2×2 small multiples):* Shows complete trajectory — when advantage appears, how it grows, how profiles differ. Richest information for a reviewer.
- *Option B (grouped bar, time-to-milestone):* Concealed a real finding — adaptive distributes effort across all 3 topics so it reaches single-topic mastery *later* than static. Using a "time to first mastery" metric made adaptive look worse. Switching to "time to 2/3 topics" masked the newly diagnosed patient (who never reached 3 topics).
- *Option C (advantage area chart):* Too abstract without the raw trajectories for reference.

Option A chosen because it honestly shows both the advantage and its nuance (delayed crossover for newly diagnosed patient), which is a stronger scientific story than cherry-picked milestones.

**Alternatives considered:** See above.

**Scripts impacted:** `figures/fig6_adaptive_vs_static.py`

**Status:** Active (supersedes single-panel design from Session 3)

---

## [2026-04-18] Figure 8 title: ax.text → fig.suptitle to prevent overlap with purple box

**Decision:** Move Figure 8's title from an `ax.text()` call inside the data axes to `fig.suptitle()` placed in the figure margin.

**Rationale:** The in-axes title at y=5.12 (data coordinates) produced a 2-line label that extended ~0.29 data units downward, overlapping with the purple "ADPKD Knowledge Gaps" box whose top edge was at y=4.88. Overlap = ~0.05 units, completely hiding the purple box text. `fig.suptitle()` renders in the figure margin and cannot overlap any axes content regardless of layout.

**Alternatives considered:**
- *Raise gap_y (move purple box down):* Insufficient — the title still occupies axes space.
- *Reduce title font size:* Degrades readability; doesn't fully solve the problem at all font sizes.

**Scripts impacted:** `figures/fig8_cedar_birch.py`

**Status:** Active

---

## [2026-04-18] Report structure: 13-page PDF via matplotlib PdfPages

**Decision:** Generate the technical report as a 13-page letter-size PDF using matplotlib `PdfPages`, with all figures embedded as PNG arrays using `fig.add_axes()` + `imshow`.

**Rationale:** Pure matplotlib ensures the report is fully reproducible from a single script (`generate_report.py`) with no external dependencies beyond the packages already required. Alternative tools (LaTeX, Word, ReportLab) would introduce new dependencies and break the one-command reproducibility guarantee.

**Alternatives considered:**
- *LaTeX:* More typographically powerful but adds a heavy dependency not otherwise needed.
- *Jupyter notebook → PDF:* Harder to version-control cleanly; cell outputs are not deterministic layout.
- *ReportLab:* Additional dependency; no advantage over matplotlib for this use case.

**Scripts impacted:** `generate_report.py`

**Status:** Active

---

## [2026-04-18] Figures 3 & 4 full-page width: PNG white-border auto-crop

**Decision:** Embed Figures 3 and 4 at full page width (8.5 inches) in the report by using numpy to detect and crop near-white border pixels from the PNG before calling `imshow`.

**Rationale:** matplotlib saves figures with internal padding. `imshow(aspect="auto")` stretches the entire image including white borders, so simply widening the embed area still showed narrow content in a wide frame. Cropping non-content pixels before embedding means the content (not padding) fills the allocated width.

**Alternatives considered:**
- *bbox_inches="tight" at figure-save time:* Applied but insufficient — matplotlib still pads.
- *Hardcode subplot margins:* Brittle; different figures have different internal layouts.

**Scripts impacted:** `generate_report.py` (`_fig_embed` helper, `page_fig3_fig4`)

**Status:** Active

---

## [2026-04-18] Figure 1 AI panel: show wrong-answer state in physician view

**Decision:** Change the physician panel in Figure 1 from showing a correct answer with a static explanation to showing a wrong answer (B: "Test urgently to qualify for tolvaptan") with a mock AI-Targeted Explanation panel driven by the item's `distractor_misconceptions` tag.

**Rationale:** The original correct-answer state was informative but missed the opportunity to prototype the most novel feature of production CEDAR-PKD — the LLM misconception-targeted feedback layer. The wrong-answer state demonstrates: (1) the post-error UI (red wrong, green correct revealed), (2) the misconception identification pipeline (distractor_misconceptions tag → misconception label), and (3) the mock LLM explanation conditioned on role and CKD stage. This directly strengthens the prototype's claim to LLM integration readiness.

**Alternatives considered:**
- *Keep correct-answer state, add AI panel to a third panel:* Figure only has two panels; no room.
- *Show AI panel in patient panel instead:* Patient view is more impactful unanswered (shows the pre-answer state); physician view post-wrong-answer is the more clinically illustrative scenario.

**Scripts impacted:** `figures/fig1_app_screenshot.py`

**Status:** Active

---

## [2026-04-18] LLM integration architecture: IRT+BKT for sequencing, LLM for explanation

**Decision:** Define the production CEDAR-PKD LLM integration as a two-layer architecture: IRT+BKT decides *what to teach next and when to stop*; LLMs decide *how to explain it* for the specific learner context.

**Rationale:** Pure LLM tutors lack a principled sequencing criterion, measurable item psychometric properties, and an auditable stopping rule. Pure IRT/BKT delivers calibrated sequencing but fixed text. The combination is defensible to both psychometrics-oriented reviewers (rigorous measurement model) and clinical education reviewers (personalized, context-aware feedback).

**Alternatives considered:**
- *LLM-only adaptive tutoring:* Rejected — no stopping criterion, no item calibration, not auditable.
- *IRT+BKT only (no LLMs):* Rejected — fixed explanations do not exploit clinical context or misconception metadata.

**Scripts impacted:** `figures/fig1_app_screenshot.py` (AI panel prototype), `generate_report.py` (page 13 LLM Vision)

**Status:** Active

---

## [2026-04-18] CAPTURE framework: not adopted for this prototype

**Decision:** Do not adopt the CAPTURE framework for this project.

**Rationale:** CAPTURE is designed for HPC/Slurm pipelines with containerised environments, reproducible data provenance via checksums, and numbered multi-stage workflows. This prototype is a single-machine figure-generation and Streamlit app codebase with no external data downloads, no containers, and no HPC execution. The numbered script convention (`fig1_`, `fig2_`, etc.) is already in use; the full CAPTURE overhead is not warranted.

**Alternatives considered:**
- *Adopt CAPTURE fully:* Over-engineered for this scope; would add tooling complexity without reproducibility benefit.
- *Adopt CAPTURE partially (numbered steps only):* Already done organically.

**Scripts impacted:** None — decision not to adopt.

**Status:** Active

---

## [2026-07-14] DOD resubmission: generate three new figures addressing reviewer concerns

**Decision:** Add three new figures (figA, figB, figC) specifically targeting critiques in the DOD PRMRP PR250279 summary statement. These are supplemental to the original fig1–fig8 and are labeled A/B/C to distinguish them as proposal-revision figures.

**Rationale:** Reviewer scores were strong (Overall 1.8 = Excellent) but three specific critiques were actionable: (1) Scientist Reviewer B questioned whether CEDAR-PKD is necessary given online resources already exist; (2) Consumer Reviewer asked whether content is tailored by patient gender; (3) Scientist Reviewer B also asked why CEDAR is needed if BIRCH-PKD already answers questions. Each figure directly rebuts one critique with prototype data.

**Alternatives considered:**
- *Address critiques in text only:* Rejected — grant reviewers respond more strongly to figures than paragraphs.
- *Modify existing figures:* Rejected — fig1–fig8 address NIH concerns; DOD concerns are distinct and should not overload existing figures.

**Scripts impacted:** `figures/figA_cedar_vs_static.py`, `figures/figB_sex_tailored_paths.py`, `figures/figC_continuum_of_care.py`, `figures/compile_all.py`

**Status:** Active

---

## [2026-07-14] Fig A: 3-column layout in data coordinates

**Decision:** Use a 3-column layout (Static | CEDAR-Patient | CEDAR-Physician) with columns drawn in matplotlib data coordinates (0–7.0 inches), not axes-fraction coordinates.

**Rationale:** Two iterations with `ax.transAxes` fraction coordinates produced columns too narrow for readable text and badges. Switching to inch-scale data coordinates gave full layout control. The 3-column structure (same question bank → different role-paths) is the correct architecture for rebutting "online resources are equivalent."

**Scripts impacted:** `figures/figA_cedar_vs_static.py`

**Status:** Active

---

## [2026-07-14] Fig B: stacked bar with score decomposition by demographic boost

**Decision:** Show recommender score breakdown (base IRT + sex boost + family-planning boost + CKD-stage boost) as stacked horizontal bars comparing female (CKD 2, family planning) vs. male (CKD 4) profiles with identical initial knowledge states.

**Rationale:** The stacked bar directly answers the consumer reviewer's gender-tailoring question with quantified boost magnitudes. Controlling for prior knowledge (same θ=0, same P(mastery)=0.30 per topic) isolates the demographic tailoring effect.

**Scripts impacted:** `figures/figB_sex_tailored_paths.py`

**Status:** Active

---

## [2026-07-14] Fig C: 3-column card layout with bottom-up vertical positioning

**Decision:** Use 3 tool-cards (CEDAR | BIRCH | ASPEN) with a patient-journey timeline banner above, and compute all vertical positions bottom-up (CARD_BOT → quote → bullets → mode → header → banner → FH) so figure height exactly matches content.

**Rationale:** Top-down fixed positioning with a large FH left 30–40% of the figure as empty white space. Bottom-up derivation of FH eliminates that. Inter-card handoff arrows were removed — the 0.17-inch inter-column gaps cannot accommodate label text without overlapping card content, and the handoff logic is already described in bullet text.

**Alternatives rejected:** staggered activation zones (v1 — too complex, elements collided), top-down fixed FH (v2/v3 — 40% empty space), inter-card arrows with 2-line labels (overlapped bullets).

**Scripts impacted:** `figures/figC_continuum_of_care.py`

**Status:** Active
