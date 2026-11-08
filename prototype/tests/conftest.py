from datetime import datetime, timedelta, timezone
import pytest
from adjudication.domain.models import ExcursionEvent, Product, Facility, Study, Alias

@pytest.fixture
def event():
    alert=datetime(2026,1,1,12,tzinfo=timezone.utc)
    return ExcursionEvent("EVT-001",alert,alert-timedelta(hours=2),"PROD-1","FAC-1",11.0,48.0,None,None,None,True,False,"ACTIONABLE excursion confirmed",True,False,{})

@pytest.fixture
def data():
    return {"products":[Product("PROD-1","Product One","Store at 2-8C","STUDY-1","TENANT-A")],"facilities":[Facility("FAC-1","Facility One","UTC","TENANT-A")],"sops":[],"studies":[Study("STUDY-1","PROD-1",True,"PASS","Up to 48 hours at 25C","TENANT-A")],"aliases":[Alias("Product One Alias","PROD-1","product")],"overrides":[]}
