# KCCS Sentinel Excursion Adjudication — Case Study Solution

This repository contains a solution for the KCCS Sentinel Excursion Adjudication case study.

It includes:

- A structured written solution in `docs/`
- Architecture, lifecycle, data-flow, deployment, and degradation diagrams in `diagrams/`
- A locally runnable adjudication prototype in `prototype/`
- Automated tests and GitHub Actions CI
- A working log of assumptions, discarded approaches, and decisions

## Windows PowerShell quick start

```powershell
git clone https://github.com/Zulfiqar78634/kccs-adjudication-case-study.git
cd kccs-adjudication-case-study

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r prototype/requirements.txt
pip install -e prototype

# Place the supplied workbook here:
# data/KCCS_Sentinel_Reference_Data_Pack.xlsx

cd prototype
pytest
cd ..

python -m adjudication.cli run --workbook data/KCCS_Sentinel_Reference_Data_Pack.xlsx --output-dir output
```

## macOS / Linux quick start

```bash
git clone https://github.com/Zulfiqar78634/kccs-adjudication-case-study.git
cd kccs-adjudication-case-study

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r prototype/requirements.txt
pip install -e prototype

# Place the supplied workbook here:
# data/KCCS_Sentinel_Reference_Data_Pack.xlsx

cd prototype
pytest
cd ..

python -m adjudication.cli run --workbook data/KCCS_Sentinel_Reference_Data_Pack.xlsx --output-dir output
```

## What the prototype does

The prototype implements the most critical and difficult component: the **case adjudication and regulatory-clock service**.

It:

- Loads the supplied workbook.
- Validates required sheets and columns.
- Normalizes timestamps to UTC.
- Creates auditable adjudication cases.
- Calculates the regulatory notification clock from `alert_ts_utc`.
- Resolves product and facility references using exact matches and reviewer-confirmed aliases.
- Selects SOP revisions effective at the alert date.
- Identifies missing or unreadable stability evidence.
- Produces deterministic recommendations.
- Records reviewer overrides and dispositions.
- Supports reopened cases without overwriting history.
- Writes JSON and CSV operational outputs.

## LLM position

The prototype uses a **bounded LLM boundary**, but the core adjudication path is deterministic.

The LLM is intended to:

- Summarize available evidence.
- Draft a reviewer-facing rationale.
- Identify uncertainties and evidence gaps.
- Propose a review action.

It does **not**:

- Calculate the regulatory clock.
- Decide a regulated disposition.
- Auto-close a case.
- Override deterministic compliance rules.
- Invent evidence or cite unavailable documents.

The default implementation uses a deterministic rationale stub so the project runs locally without an API key. A production LLM integration can be added behind the same interface, with prompt/model versioning, source-grounding validation, and human approval.

## Repository layout

```text
docs/        Written case-study deliverables
diagrams/    Mermaid architecture and workflow diagrams
data/        Supplied workbook location; workbook is gitignored
prototype/   Runnable adjudication service, tests, and outputs
scripts/     Local utilities
.github/     CI and contribution workflow
```
