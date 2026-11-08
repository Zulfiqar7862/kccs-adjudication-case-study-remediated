# Working Prototype

This prototype implements the **case adjudication and regulatory-clock service**.

## Windows PowerShell quick start

Run these commands from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r prototype/requirements.txt
pip install -e prototype
```

Place the supplied workbook here:

```text
data/KCCS_Sentinel_Reference_Data_Pack.xlsx
```

Then run the tests and prototype from the repository root:

```powershell
cd prototype
pytest
cd ..
python -m adjudication.cli run --workbook data/KCCS_Sentinel_Reference_Data_Pack.xlsx --output-dir output
```

## macOS / Linux quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r prototype/requirements.txt
pip install -e prototype

cd prototype
pytest
cd ..
python -m adjudication.cli run --workbook data/KCCS_Sentinel_Reference_Data_Pack.xlsx --output-dir output
```

## Outputs

- `output/adjudication_report.json`
- `output/adjudication_summary.csv`
- `output/case_audit_log.csv`
- `output/evidence_gaps.csv`
- `output/run_manifest.json`

## Design

- The regulatory clock is calculated from `alert_ts_utc`.
- Source values and canonical resolutions are separately traceable.
- Missing or unreadable stability evidence creates an evidence gap, not an invented outcome.
- Reopened cases are new adjudication attempts linked to the original case.
- Every material workflow transition is recorded as an audit event.
- The LLM boundary is optional and stubbed by default.
