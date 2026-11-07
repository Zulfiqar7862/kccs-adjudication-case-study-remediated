.PHONY: install test run clean

install:
	python -m pip install -r prototype/requirements.txt

test:
	cd prototype && pytest

run:
	cd prototype && python -m adjudication.cli run --workbook ../data/KCCS_Sentinel_Reference_Data_Pack.xlsx --output-dir output

clean:
	rm -rf .pytest_cache .venv
