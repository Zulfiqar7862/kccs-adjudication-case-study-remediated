from dataclasses import replace
from copy import deepcopy
from adjudication.workflow.case_service import CaseService
from adjudication.audit.event_store import audit_rows
from adjudication.cli import run
import json

def test_historical_import_not_new_signature(event,data):
    c=CaseService(data).create_case(replace(event,disposition='RELEASE',raw={'tenant_code':'TENANT-A','reviewer_id':'QA-A','days_to_disposition':2}),event.alert_ts_utc)
    imp=next(x for x in c.events if x.event_type=='HISTORICAL_DISPOSITION_IMPORTED')
    assert imp.actor=='source_import' and imp.payload['source_reviewer_id']=='QA-A'
    assert not any(x.event_type=='DISPOSITION_RECORDED' for x in c.events)
    assert c.state=='PENDING_REVIEWER'

def test_audit_export_is_defensive_snapshot(event,data):
    c=CaseService(data).create_case(event,event.alert_ts_utc);before=deepcopy(c.events[0].payload)
    export=audit_rows([c]);export[0]['payload']['source_event_id']='MUTATED'
    assert c.events[0].payload==before

def test_real_manifest_and_fixed_replay(workbook_data,tmp_path):
    from pathlib import Path
    import os
    p=Path(os.environ.get('KCCS_WORKBOOK',Path(__file__).resolve().parents[3]/'data/KCCS_Sentinel_Reference_Data_Pack.xlsx'))
    for sub in ['one','two']:run(p,tmp_path/sub,as_at='2026-11-08T06:00:00+00:00')
    m=json.loads((tmp_path/'one/run_manifest.json').read_text())
    assert m['workbook_sha256']=='9fe3fad7d0f77a5fbdaa0f8ce70336a911a8725d38d057b9d9d777c06ea57db3'
    assert m['code_commit'] and m['as_at'] and m['reference_bundle']
    for name in ['adjudication_report.json','case_audit_log.csv','adjudication_summary.csv','evidence_gaps.csv','run_manifest.json']:
        assert (tmp_path/'one'/name).read_bytes()==(tmp_path/'two'/name).read_bytes()
