"""
figures/figE_personalization.py
Figure E — CEDAR-PKD Personalization (combined two-panel figure)

Panel A: CEDAR-PKD vs. generic online resources
  Addresses DOD Scientist Reviewer B: "CEDAR-PKD does not seem exciting or
  necessary given the availability of various educational resources online."

Panel B: Sex and demographic tailoring — recommender score breakdown
  Addresses DOD Consumer Reviewer: "Whether information will be tailored by
  patient gender" and Scientist Reviewer A: "Sex as biological variable not
  explicitly addressed."

Combines former figA and figB into one figure.

Generation
----------
    python figures/figE_personalization.py
"""

import os, sys
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from figures.style import apply_cedar_style, save_figure, GRAY_MED, GRAY_DARK
from models.recommender import (_is_eligible, BOOST_SEX_SPECIFIC,
                                BOOST_SEX_FEMALE_SPECIFIC, BOOST_SEX_MALE_SPECIFIC,
                                BOOST_FAMILY_PLANNING, BOOST_DISEASE_STAGE)
from simulation.simulate import load_content, run_simulation

# ── Colours ───────────────────────────────────────────────────────────────────
CEDAR_DARK   = "#2C3E50"
WHITE        = "#FFFFFF"
CEDAR_BLUE   = "#2980B9"

# Panel A
STATIC_HDR   = "#717D7E"
STATIC_BG    = "#EAECEE"
STATIC_Q_FC  = "#D5D8DC"
STATIC_Q_EC  = "#A6ACAF"
PATIENT_C    = "#C0392B"
PHYSICIAN_C  = "#1A7D5A"
BADGE_SEX    = "#C0392B"
BADGE_FP     = "#7D3C98"
BADGE_STAGE  = "#CA6F1E"
BADGE_ROLE   = "#1A5276"
CEDAR_LT_P   = "#FDEDEC"
CEDAR_LT_PH  = "#E9F7EF"
GRAY_MED_A   = "#AAB7B8"
GRAY_DARK_A  = "#566573"

# Panel B
FEMALE_C  = "#E85D8A"
MALE_C    = "#3D7EBF"
BASE_C    = "#BDC3C7"
SEX_C      = "#C0392B"   # female-sex-specific
SEX_MALE_C = "#1A5276"   # male-sex-specific
FP_C       = "#8E44AD"
STAGE_C    = "#E67E22"

# ── Panel A layout constants (data units: xlim=0–7, ylim=0–5.0) ───────────────
PA_FW, PA_FH = 7.0, 5.0

C1_X, C1_W = 0.15, 1.96
C2_X, C2_W = 2.27, 2.15
C3_X, C3_W = 4.58, 2.25

P_BOT = 1.10
P_TOP = 4.78
HDR_H = 0.50
Q_H   = 0.38
BDG_H = 0.16
BDG_G = 0.05
ROW_G = 0.12
Q_TOP = P_TOP - HDR_H - 0.14


# ── Panel A primitives ────────────────────────────────────────────────────────

def _rbox(ax, x, y, w, h, fc, ec, lw=0.9, r=0.08):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle=f"round,pad={r}",
        facecolor=fc, edgecolor=ec, linewidth=lw,
    ))


def _t(ax, x, y, s, **kw):
    ax.text(x, y, s, **kw)


def _arr(ax, x, y0, y1, color, lw=0.9):
    ax.annotate("", xy=(x, y1), xytext=(x, y0),
                arrowprops=dict(arrowstyle="-|>", color=color,
                                lw=lw, mutation_scale=6))


def _col_header(ax, cx, cy, cw, ch, title, sub, hdr_fc):
    _rbox(ax, cx, cy, cw, ch, fc=hdr_fc, ec=hdr_fc, lw=0, r=0.08)
    _t(ax, cx + cw/2, cy + ch*0.62, title,
       ha="center", va="center", fontsize=8.0, color=WHITE, fontweight="bold")
    _t(ax, cx + cw/2, cy + ch*0.24, sub,
       ha="center", va="center", fontsize=5.8, color=WHITE, fontstyle="italic")


def _q_box(ax, cx, cy_top, cw, label, fc, ec, inset=0.08):
    x, y, w = cx + inset, cy_top - Q_H, cw - 2*inset
    _rbox(ax, x, y, w, Q_H, fc=fc, ec=ec, lw=0.9, r=0.07)
    _t(ax, x + w/2, y + Q_H/2, label,
       ha="center", va="center", fontsize=6.0, color=CEDAR_DARK)
    return y


def _badges(ax, cx, box_bottom, cw, badges, inset=0.08):
    strip_top = box_bottom - BDG_G
    strip_bot = strip_top - BDG_H
    bx = cx + inset
    avail_w = cw - 2*inset
    n = len(badges)
    bw = (avail_w - (n-1)*0.06) / n
    for i, (lbl, fc) in enumerate(badges):
        bxi = bx + i*(bw + 0.06)
        _rbox(ax, bxi, strip_bot, bw, BDG_H, fc=fc, ec=fc, lw=0, r=0.04)
        _t(ax, bxi + bw/2, strip_bot + BDG_H/2, lbl,
           ha="center", va="center", fontsize=4.8, color=WHITE, fontweight="bold")
    return strip_bot


def _column(ax, cx, cw, questions, fc, ec, hdr_fc, panel_fc,
            hdr_title, hdr_sub, show_badges=True):
    _rbox(ax, cx, P_BOT, cw, P_TOP - P_BOT, fc=panel_fc, ec=ec, lw=1.0, r=0.10)
    _col_header(ax, cx, P_TOP - HDR_H, cw, HDR_H, hdr_title, hdr_sub, hdr_fc)
    cur_top = Q_TOP
    for i, (label, badges) in enumerate(questions):
        box_bot = _q_box(ax, cx, cur_top, cw, label, fc=fc, ec=ec)
        if show_badges and badges:
            badge_bot = _badges(ax, cx, box_bot, cw, badges)
            next_top  = badge_bot - ROW_G
        else:
            next_top  = box_bot - BDG_G - BDG_H - ROW_G
        if i < len(questions) - 1:
            _arr(ax, cx + cw/2, next_top + ROW_G/2, next_top + 0.03, ec)
        cur_top = next_top


# ── Panel A content ───────────────────────────────────────────────────────────

STATIC_QS = [
    ("What is ADPKD and how common is it?",   []),
    ("Which genes cause ADPKD (PKD1, PKD2)?", []),
    ("What are the symptoms of ADPKD?",        []),
    ("How is ADPKD diagnosed?",                []),
]

PATIENT_QS = [
    ("ADPKD complications in women:\naneurysm & liver cyst risk",
     [("+Sex-specific", BADGE_SEX)]),
    ("Family planning & IVF/PGT\noptions with ADPKD",
     [("+Sex-specific", BADGE_SEX), ("+Family planning", BADGE_FP)]),
    ("Genetic testing value for\nreproductive decisions",
     [("+Family planning", BADGE_FP)]),
    ("PKD2 prognosis at your\nCKD Stage 2",
     [("+CKD stage match", BADGE_STAGE)]),
]

PHYSICIAN_QS = [
    ("PKD1 vs. PKD2: severity,\nprognosis & management",
     [("+Physician only", BADGE_ROLE)]),
    ("Tolvaptan eligibility criteria\nby CKD stage",
     [("+Physician only", BADGE_ROLE), ("+CKD stage match", BADGE_STAGE)]),
    ("Counselling patients on\npreimplantation genetic testing",
     [("+Sex-specific", BADGE_SEX), ("+Family planning", BADGE_FP)]),
    ("Barriers to genetic testing\nin nephrology practice",
     [("+Physician only", BADGE_ROLE)]),
]


# ── Panel B helpers ───────────────────────────────────────────────────────────

FEMALE_PROFILE = {
    "id": "female_early_family_planning", "role": "patient",
    "sex": "female", "family_planning": True, "disease_stage": 2,
    "theta": 0.0,
    "label": "Female Patient · CKD Stage 2\nFamily planning = Yes",
    "color": FEMALE_C,
}

MALE_PROFILE = {
    "id": "male_advanced", "role": "patient",
    "sex": "male", "family_planning": False, "disease_stage": 4,
    "theta": 0.0,
    "label": "Male Patient · CKD Stage 4\nFamily planning = No",
    "color": MALE_C,
}

INITIAL_STATE = {"kidney_basics": 0.30, "adpkd_genetics": 0.30, "adpkd_diagnosis": 0.30}

Q_LABELS = {
    "q_1_2_01": "ADPKD prevalence (1 in 1,000)",
    "q_1_2_02": "PKD1 & PKD2 causative genes",
    "q_1_2_03": "Extra-renal manifestations",
    "q_1_2_04": "Diagnosis delay & mortality risk",
    "q_1_2_05": "Cyst growth mechanism",
    "q_1_2_06": "Inheritance risk for children",
    "q_1_3_01": "Autosomal dominant inheritance",
    "q_1_3_02": "PKD1 vs. PKD2: disease severity",
    "q_1_3_03": "De novo mutations in ADPKD",
    "q_1_3_04": "Seven ADPKD-associated genes",
    "q_1_3_05": "PKD2 prognosis comparison",
    "q_1_3_06": "Genetic testing value if already diagnosed",
    "q_2_3_01": "PGT indications by patient scenario",
    "q_2_3_02": "Variant of Uncertain Significance (VUS)",
    "q_2_3_03": "Reproductive options with ADPKD",
    "q_2_3_04": "Barriers to genetic testing",
    "q_2_3_05": "IVF/PGT options for young woman",
    "q_2_3_06": "Variant classification system",
    "q_2_3_07": "Genetic testing value at Stage 4–5",
    "q_2_3_08": "ADPKD complications in women",
}


def _score_breakdown(q, a_est, profile):
    topic = q["topic"]
    p_mastery = INITIAL_STATE.get(topic, 0.30)
    base = (1.0 - p_mastery) * float(a_est)
    tags = q.get("demographic_tags", {})
    b_sex_f = b_sex_m = b_fp = b_stage = 0.0
    # Legacy generic sex tag
    if tags.get("sex_specific", False) and profile.get("sex") in ("female", "male"):
        b_sex_f = BOOST_SEX_SPECIFIC
    # Granular female-specific tag
    if tags.get("sex_female_specific", False) and profile.get("sex") == "female":
        b_sex_f = BOOST_SEX_FEMALE_SPECIFIC
    # Granular male-specific tag
    if tags.get("sex_male_specific", False) and profile.get("sex") == "male":
        b_sex_m = BOOST_SEX_MALE_SPECIFIC
    if tags.get("family_planning_relevant", False) and profile.get("family_planning", False):
        b_fp = BOOST_FAMILY_PLANNING
    stage_list = tags.get("disease_stage_relevant", [])
    if stage_list:
        user_stage = profile.get("disease_stage")
        if user_stage is not None and int(user_stage) in [int(s) for s in stage_list]:
            b_stage = BOOST_DISEASE_STAGE
    return base, b_sex_f, b_sex_m, b_fp, b_stage


def _build_ranked(questions, irt_dict, profile, top_n=6):
    rows = []
    for q in questions:
        if not _is_eligible(q, profile):
            continue
        # Hard-filter stage-tagged items: only show to patients whose stage matches
        stage_list = q.get("demographic_tags", {}).get("disease_stage_relevant", [])
        if stage_list:
            user_stage = profile.get("disease_stage")
            if user_stage is None or int(user_stage) not in [int(s) for s in stage_list]:
                continue
        a_est = float(irt_dict.get(q["id"], {}).get("a_estimated", 1.0))
        base, b_sex_f, b_sex_m, b_fp, b_stage = _score_breakdown(q, a_est, profile)
        rows.append({
            "label":  Q_LABELS.get(q["id"], q["id"]),
            "base":   base,
            "b_sex_f": b_sex_f,
            "b_sex_m": b_sex_m,
            "b_fp":   b_fp,
            "b_stage": b_stage,
            "total":  base + b_sex_f + b_sex_m + b_fp + b_stage,
        })
    df = pd.DataFrame(rows).sort_values("total", ascending=False).head(top_n)
    return df[::-1]


def _draw_bar_panel(ax, df, profile, xlim=2.0, ref_base=None):
    color = profile["color"]
    y_pos = np.arange(len(df))

    left = df["base"].copy()
    ax.barh(y_pos, df["base"], color=BASE_C, height=0.55,
            label="Base (IRT discrimination × topic gap)")

    ax.barh(y_pos, df["b_sex_f"], left=left, color=SEX_C, height=0.55,
            label=f"+Female sex-specific ({BOOST_SEX_FEMALE_SPECIFIC:.2f})")
    left = left + df["b_sex_f"]

    ax.barh(y_pos, df["b_sex_m"], left=left, color=SEX_MALE_C, height=0.55,
            label=f"+Male sex-specific ({BOOST_SEX_MALE_SPECIFIC:.2f})")
    left = left + df["b_sex_m"]

    ax.barh(y_pos, df["b_fp"], left=left, color=FP_C, height=0.55,
            label=f"+Family planning ({BOOST_FAMILY_PLANNING:.2f})")
    left = left + df["b_fp"]

    ax.barh(y_pos, df["b_stage"], left=left, color=STAGE_C, height=0.55,
            label=f"+CKD stage match ({BOOST_DISEASE_STAGE:.2f})")

    for i, row in enumerate(df.itertuples()):
        inside = row.total > xlim * 0.80
        xpos   = row.total - 0.04 if inside else row.total + 0.02
        ha     = "right" if inside else "left"
        fc     = WHITE if inside else CEDAR_DARK
        ax.text(xpos, i, f"{row.total:.2f}", va="center", ha=ha, fontsize=6.5, color=fc)

    ax.set_yticks(y_pos)
    wrapped = [textwrap.fill(lbl, width=22) for lbl in df["label"]]
    ax.set_yticklabels(wrapped, fontsize=6.8)
    ax.set_xlabel("Recommender Score", fontsize=7.0)
    ax.set_xlim(0, xlim)
    ax.set_title(profile["label"], fontsize=8.0, fontweight="bold", color=color, pad=4)

    for i, (_, row) in enumerate(df.iterrows()):
        if row["b_sex_f"] + row["b_sex_m"] + row["b_fp"] + row["b_stage"] > 0:
            ax.get_yticklabels()[i].set_fontweight("bold")
            ax.get_yticklabels()[i].set_color(color)

    max_base = ref_base if ref_base is not None else df["base"].max()
    ax.axvline(max_base, color=GRAY_MED, lw=0.8, linestyle=":",
               label=f"Unboosted ceiling (best IRT score = {max_base:.2f})")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.25, linestyle="--", linewidth=0.5)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    apply_cedar_style()

    irt_csv = os.path.join(_ROOT, "outputs", "irt_params.csv")
    if not os.path.exists(irt_csv):
        run_simulation(verbose=False)
    modules_data, _ = load_content()
    questions = modules_data["questions"]
    irt_df = pd.read_csv(irt_csv)
    irt_dict = {r["question_id"]: {"a_estimated": r["a_estimated"],
                                    "b_estimated": r["b_estimated"]}
                for _, r in irt_df.iterrows()}

    df_female = _build_ranked(questions, irt_dict, FEMALE_PROFILE, top_n=6)
    df_male   = _build_ranked(questions, irt_dict, MALE_PROFILE,   top_n=6)

    # ── Figure layout ─────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(7.0, 9.2))
    gs = gridspec.GridSpec(2, 1, figure=fig,
                           height_ratios=[5.0, 3.8],
                           hspace=0.07,
                           top=0.98, bottom=0.13, left=0.01, right=0.99)

    # ── Panel A ───────────────────────────────────────────────────────────────
    ax_a = fig.add_subplot(gs[0])
    ax_a.set_xlim(0, PA_FW)
    ax_a.set_ylim(P_BOT - 0.18, PA_FH)
    ax_a.axis("off")

    # Column 1 — Static
    _column(ax_a, C1_X, C1_W, STATIC_QS,
            fc=STATIC_Q_FC, ec=STATIC_Q_EC,
            hdr_fc=STATIC_HDR, panel_fc=STATIC_BG,
            hdr_title="Generic Online Resource",
            hdr_sub="Same content for every learner",
            show_badges=False)
    _t(ax_a, C1_X + C1_W/2, P_BOT + 0.10,
       "[!] No role-filter · No demographic tailoring",
       ha="center", va="center", fontsize=5.2, color=STATIC_HDR, fontstyle="italic")

    # VS. divider
    vx = C1_X + C1_W + (C2_X - C1_X - C1_W) / 2
    ax_a.plot([vx, vx], [P_BOT+0.3, P_TOP-0.3], color=GRAY_MED_A, lw=0.8, linestyle="--")
    _t(ax_a, vx, (P_BOT + P_TOP)/2, "VS.",
       ha="center", va="center", fontsize=11.5, color=GRAY_DARK_A, fontweight="bold",
       bbox=dict(facecolor=WHITE, edgecolor=GRAY_MED_A, boxstyle="round,pad=0.18", linewidth=0.8))

    # Column 2 — CEDAR Patient
    _column(ax_a, C2_X, C2_W, PATIENT_QS,
            fc=WHITE, ec=PATIENT_C,
            hdr_fc=PATIENT_C, panel_fc=CEDAR_LT_P,
            hdr_title="CEDAR-PKD: Patient",
            hdr_sub="Female · CKD Stage 2 · Family planning")
    _t(ax_a, C2_X + C2_W/2, P_BOT + 0.10,
       "[+] Role-filtered · Sex-tailored · Stage-matched",
       ha="center", va="center", fontsize=5.2, color=PATIENT_C, fontstyle="italic")

    # Column 3 — CEDAR Physician
    _column(ax_a, C3_X, C3_W, PHYSICIAN_QS,
            fc=WHITE, ec=PHYSICIAN_C,
            hdr_fc=PHYSICIAN_C, panel_fc=CEDAR_LT_PH,
            hdr_title="CEDAR-PKD: Clinician",
            hdr_sub="Experienced PCP · Role-filtered")
    _t(ax_a, C3_X + C3_W/2, P_BOT + 0.10,
       "[+] Role-filtered · High-discrimination items first",
       ha="center", va="center", fontsize=5.2, color=PHYSICIAN_C, fontstyle="italic")

    # Shared item bank callout
    _rbox(ax_a, C2_X, P_TOP + 0.05, C3_X + C3_W - C2_X, 0.20,
          fc="#D6EAF8", ec=CEDAR_BLUE, lw=0.8, r=0.05)
    _t(ax_a, (C2_X + C3_X + C3_W)/2, P_TOP + 0.15,
       "Same 20-item ADPKD question bank  —  entirely different personalised sequence per learner",
       ha="center", va="center", fontsize=6.2, color=CEDAR_DARK)

    # Panel A badge legend
    legend_items = [
        (BADGE_SEX,   "+Sex-specific"),
        (BADGE_FP,    "+Family planning"),
        (BADGE_STAGE, "+CKD stage match"),
        (BADGE_ROLE,  "+Clinician only"),
    ]
    lx, ly = 2.27, P_BOT - 0.10
    _t(ax_a, lx - 0.05, ly + 0.05, "Boost key:",
       ha="left", va="center", fontsize=6.2, color=CEDAR_DARK, fontweight="bold")
    bx = lx + 0.78
    for fc, label in legend_items:
        _rbox(ax_a, bx, ly - 0.01, 0.13, 0.13, fc=fc, ec=fc, lw=0, r=0.03)
        _t(ax_a, bx + 0.17, ly + 0.05, label,
           ha="left", va="center", fontsize=5.8, color=CEDAR_DARK)
        bx += 1.02

    # ── Panel B — manually positioned to avoid label collisions ──────────────
    sp      = gs[1].get_position(fig)
    lmargin = 0.09   # left space for female panel y-axis labels (2-line wrapped)
    gap     = 0.16   # space between panels (includes male panel y-axis labels)
    pw      = (sp.x1 - sp.x0 - lmargin - gap) / 2
    ph      = sp.y1 - sp.y0 - 0.09
    pb      = sp.y0 + 0.09
    ax_b1 = fig.add_axes([sp.x0 + lmargin,              pb, pw, ph])
    ax_b2 = fig.add_axes([sp.x0 + lmargin + pw + gap,   pb, pw, ph])

    shared_ref = max(df_female["base"].max(), df_male["base"].max())
    _draw_bar_panel(ax_b1, df_female, FEMALE_PROFILE, xlim=1.9, ref_base=shared_ref)
    _draw_bar_panel(ax_b2, df_male,   MALE_PROFILE,   xlim=2.1, ref_base=shared_ref)

    h1, l1 = ax_b1.get_legend_handles_labels()
    h2, l2 = ax_b2.get_legend_handles_labels()
    seen = set(); handles_all = []; labels_all = []
    for h, l in zip(h1 + h2, l1 + l2):
        if l not in seen:
            seen.add(l); handles_all.append(h); labels_all.append(l)
    fig.legend(handles_all, labels_all, loc="upper center", ncol=3,
               fontsize=6.0, framealpha=0.9,
               bbox_to_anchor=(0.5, pb - 0.05), borderpad=0.5)

    # ── Panel labels A / B ────────────────────────────────────────────────────
    pos_a  = ax_a.get_position()
    pos_b1 = ax_b1.get_position()
    lx_lbl = pos_a.x0 - 0.01
    fig.text(lx_lbl, pos_a.y1 + 0.002, "A",
             fontsize=11, fontweight="bold", va="bottom", ha="right", color=CEDAR_DARK)
    fig.text(lx_lbl, pos_b1.y1 + 0.002, "B",
             fontsize=11, fontweight="bold", va="bottom", ha="right", color=CEDAR_DARK)

    out_dir = os.path.join(_ROOT, "outputs")
    os.makedirs(out_dir, exist_ok=True)
    base_path = os.path.join(out_dir, "figE_personalization")
    fig.savefig(f"{base_path}.png", dpi=300, bbox_inches="tight", pad_inches=0.02, facecolor="white")
    fig.savefig(f"{base_path}.pdf", bbox_inches="tight", pad_inches=0.02, facecolor="white")
    plt.close(fig)
    print("Figure E complete.")


if __name__ == "__main__":
    main()
