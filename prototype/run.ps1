# Run from the repository root.
# Usage: .\prototype\run.ps1 -Workbook "data/KCCS_Sentinel_Reference_Data_Pack.xlsx"
param(
  [string]$Workbook = "data/KCCS_Sentinel_Reference_Data_Pack.xlsx",
  [string]$OutputDir = "output"
)

if (-not (Test-Path $Workbook)) {
  Write-Error "Workbook not found: $Workbook"
  exit 1
}

python -m adjudication.cli run --workbook $Workbook --output-dir $OutputDir
