# KCCS — offline evidence-eligibility remediation

This is a deterministic **offline prototype**, not a production adjudication platform. It reads a confidential extract, resolves source-row candidates, flags uncertainty, exports original/reopened attempts and advisory review actions. It does not sign dispositions, auto-close alerts, notify regulators or call a model. All regulated decisions remain human responsibilities.

## Install and test (from repository root)
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r prototype/requirements.txt -e prototype
python -m pytest prototype/tests
# Optional confidential input, never commit it:
export KCCS_WORKBOOK=/absolute/path/KCCS_Sentinel_Reference_Data_Pack.xlsx
python -m pytest prototype/tests
python -m adjudication.cli run --workbook "$KCCS_WORKBOOK" --output-dir prototype/output --as-at 2026-11-08T12:00:00+00:00
```
Without the workbook, workbook-backed tests skip; synthetic safety tests still execute. Alternatively put it in `data/KCCS_Sentinel_Reference_Data_Pack.xlsx`. Keep all real replay exports local and ignored.

PowerShell: create `.venv`, activate `.\.venv\Scripts\Activate.ps1`, run the same pip/pytest commands, then from root:
```powershell
./prototype/run.ps1 -Workbook "C:\private\KCCS_Sentinel_Reference_Data_Pack.xlsx" -OutputDir "prototype/output" -AsAt "2026-11-08T12:00:00+00:00"
```
Linux PowerShell was exercised; native Windows and Docker are not validated. Docker installs the actual package; mount private data read-only and an output volume if using it. GNU make recipes: `make setup`, `make test`, `make run`, `make e2e`; Make itself was unavailable in the remediation environment. Their equivalent Python commands were exercised.

## Safe synthetic CLI without private data
```bash
python -m adjudication.synthetic prototype/output/synthetic.xlsx
python -m adjudication.cli run --workbook prototype/output/synthetic.xlsx --output-dir prototype/output/synthetic --as-at 2026-01-10T12:00:00+00:00
```
CI executes this synthetic CLI, tests, Bandit, pip-audit and Gitleaks. Those workflow definitions are real, but no remote workflow run or publication was performed during remediation.

## Output contract
Seven files: `adjudication_report.json`, `case_summary.csv`, `evidence_gaps.csv`, `audit_log.jsonl`, `run_manifest.json`, `rejected_rows.csv`, `comparison_report.json`. The supplied extract yields 420 source events and 481 attempts (61 reopen flags), not 481 independent regulatory clocks. Read the actual filenames in `cli.py` if integrating; all are local mutable exports. Fixed input, revision and `--as-at` reproduce bytes; this is not bitemporal reconstruction or seven-year immutable retention.

`historical_disposition` and `HISTORICAL_DISPOSITION_IMPORTED` describe source history; `new_approval` is always null. Compatibility field `proposed_disposition` contains an **advisory review action**, not a regulated outcome. Source `NON_ACTIONABLE` is parsed but is never permission to auto-close. The comparison report intentionally does not equate advisory actions with historical disposition labels or claim model accuracy.

Notification applicability, qualified policy, source receipt evidence and assessment are separate. Unidentified jurisdictions remain `POLICY_UNKNOWN` even when the extract supplies a numeric window; a separate extracted-window comparison is not a legal breach finding. Brazil/India/EU policies require explicit applicability/jurisdiction, and the unidentified US programme requires a named timezone/business calendar/holiday set/cutoff. No universal 72-hour fallback.

Tenant-scoped identifiers preserve all product rows, aliases remain observations/candidates, study purpose/presentation/ownership are checked, and SOP overlap/unknown site/annexure limits abstain. Real study bodies, approvals and legal policy bindings still require qualification. No cross-tenant precedent index is implemented; tenant-safe lookup of the scoped master is not proof of Clause22 compliance for a future index.

## Boundaries and evidence
See `docs/REMEDIATION_PLAN.md`, `docs/08-validation-and-test-strategy.md`, `docs/09-risks-assumptions-and-open-questions.md`, and `docs/working-log/remediation-retrospective.md`. Architecture diagrams describe target design, not deployed components. No scripts/ directory or running web service is provided. The separate remediation report contains actual command logs, revision identity and named-case traces; no confidential pack or output belongs in this source archive.
