import pytest
from adjudication.cli import load_workbook

def test_workbook_loader_schema_error(tmp_path):
    import pandas as pd
    p=tmp_path/"bad.xlsx"; pd.DataFrame({"wrong":[1]}).to_excel(p,index=False)
    with pytest.raises(Exception): load_workbook(p)
