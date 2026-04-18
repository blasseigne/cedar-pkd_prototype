# CEDAR-PKD Prototype

**Core Education Development Adaptive Resource for PKD**

A prototype Adaptive Learning Engine (ALE) for ADPKD education, built to generate preliminary data for NIH R01 resubmission (1R01DK149254).

## Purpose

This prototype addresses reviewer concerns by demonstrating:
- A working 2-parameter logistic (2PL) IRT-based item scoring system
- Bayesian Knowledge Tracing (BKT) per-topic mastery tracking
- A content recommender incorporating role, demographics, disease stage, and knowledge state
- An interactive Streamlit web application with patient and physician views
- Simulated learner trajectories showing adaptive vs. static learning path efficiency

## Structure

```
cedar-pkd_prototype/
├── content/              # Module and question data, user profile definitions
├── models/               # IRT, BKT, and recommender engines
├── simulation/           # Simulation pipeline for generating figure data
├── figures/              # Figure generation scripts (one per figure)
├── app/                  # Streamlit application
├── outputs/              # Generated figures (300 DPI PNG + PDF)
└── requirements.txt
```

## Figures Generated

| Figure | Description | Reviewer Concern Addressed |
|--------|-------------|---------------------------|
| Fig 1  | Prototype screenshots (patient vs. physician views) | No ALE proof-of-concept; dense UI |
| Fig 2  | IRT Item Characteristic Curves (2PL model) | IRT model unspecified |
| Fig 3  | Item parameter table (difficulty, discrimination, metadata) | No item calibration detail |
| Fig 4  | Learning objectives taxonomy (Bloom's levels + IRT difficulty) | No taxonomy defined |
| Fig 5  | Simulated learner trajectories (4 user profiles) | Adaptive logic not validated |
| Fig 6  | Adaptive vs. static knowledge gain comparison | Why individualized learning helps |
| Fig 7  | Demographically-tailored learning paths | No demographic variables |
| Fig 8  | CEDAR vs. BIRCH differentiation schematic | CEDAR necessity questioned |

## Setup

```bash
pip install -r requirements.txt
```

## Running the App

```bash
streamlit run app/cedar_app.py
```

## Generating All Figures

```bash
python figures/compile_all.py
```

## Context

- **Disease**: Autosomal Dominant Polycystic Kidney Disease (ADPKD)
- **Grant**: NIH R01DK149254 resubmission
- **PI**: Brittany N. Lasseigne, University of Alabama at Birmingham
- **Collaborators**: Michal Mrug MD, Matthew Might PhD
