from dataclasses import replace
from datetime import datetime,timezone
import pytest
from adjudication.temporal.effective_dating import select_effective
from adjudication.domain.models import SOP
from adjudication.workflow.case_service import CaseService

def test_overlap_abstains():
    t=datetime(2026,1,1,tzinfo=timezone.utc)
    with pytest.raises(ValueError):select_effective([SOP('S','1',t,None,None),SOP('S','2',t,None,None)],t,'S')

def test_real_case_only_kaveri_sop_candidates(workbook_data):
    e=next(e for e in workbook_data['events'] if e.event_id=='EXC-107133')
    c=CaseService(workbook_data).create_case(e,e.alert_ts_utc)
    p=next(x.payload for x in c.events if x.event_type=='RECOMMENDATION_GENERATED')
    assert all(x['tenant_code']=='T-KAVERI' for x in p['sop_resolution']['candidates'])
    assert 'SOP_REVISION_CONFLICT' in p['sop_resolution']['issues']
    assert p['applicable_sop'] is None

def test_wrong_tenant_missing_scope_is_not_applicable(event,data):
    t=datetime(2020,1,1,tzinfo=timezone.utc)
    c=CaseService({**data,'sops':[SOP('S','1',t,None,None)]}).create_case(replace(event,raw={'tenant_code':'B'}),event.alert_ts_utc)
    assert any(g['gap_type']=='SOP_MISSING' for g in c.gaps)
