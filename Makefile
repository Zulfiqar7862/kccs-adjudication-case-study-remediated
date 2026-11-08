.PHONY: setup install test run e2e clean
PYTHON ?= python3
VENV_PY = .venv/bin/python
setup:
	$(PYTHON) -m venv .venv
	$(VENV_PY) -m pip install -r prototype/requirements.txt -e prototype
install:
	$(PYTHON) -m pip install -r prototype/requirements.txt -e prototype
test:
	$(VENV_PY) -m pytest prototype/tests
run:
	$(VENV_PY) -m adjudication.cli run --workbook data/KCCS_Sentinel_Reference_Data_Pack.xlsx --output-dir prototype/output
e2e:
	$(VENV_PY) -m adjudication.synthetic prototype/output/synthetic.xlsx
	$(VENV_PY) -m adjudication.cli run --workbook prototype/output/synthetic.xlsx --output-dir prototype/output/synthetic --as-at 2026-01-10T12:00:00+00:00
clean:
	$(PYTHON) -c "import shutil; shutil.rmtree('.pytest_cache', ignore_errors=True)"
