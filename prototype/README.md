# Working Prototype

This prototype implements the **case adjudication and regulatory-clock service**.

## Run

```bash
python -m adjudication.cli run \\
  --workbook ../data/KCCS_Sentinel_Reference_Data_Pack.xlsx \\
  --output-dir output
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
