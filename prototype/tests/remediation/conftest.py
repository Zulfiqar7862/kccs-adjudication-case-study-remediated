from pathlib import Path
import os
import pytest
from adjudication.cli import load_workbook
@pytest.fixture(scope='session')
def workbook_data():
    p=Path(os.environ.get('KCCS_WORKBOOK',Path(__file__).resolve().parents[3]/'data/KCCS_Sentinel_Reference_Data_Pack.xlsx'))
    if not p.exists():pytest.skip('Confidential workbook not supplied; synthetic safety tests still run')
    return load_workbook(p)
