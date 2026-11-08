import json,subprocess,sys
from pathlib import Path
from adjudication.ingestion.workbook_loader import to_bool,to_float

def test_unknown_boolean_is_unknown():
    assert to_bool(None) is None and to_bool('unexpected') is None

def test_nonfinite_numeric_not_valid():
    assert to_float(float('inf')) is None

def test_real_offsets_and_named_trace(workbook_data):
    assert all(q['utc_offset'] is not None and q['utc_start'] for q in workbook_data['reviewer_queue'])
    from adjudication.workflow.case_service import CaseService
    s=CaseService(workbook_data)
    for eid in ['EXC-107133','EXC-112352','EXC-110574']:
        e=next(e for e in workbook_data['events'] if e.event_id==eid);c=s.create_case(e,e.alert_ts_utc)
        assert c.recommendation['auto_close_authorized'] is False
        p=next(x.payload for x in c.events if x.event_type=='RECOMMENDATION_GENERATED')
        assert p['product_resolution']['tenant_code']==e.raw['tenant_code']

def test_synthetic_cli_all_files_and_reject_ledger(tmp_path):
    from adjudication.synthetic import write_workbook
    from adjudication.cli import load_workbook
    p=tmp_path/'synthetic.xlsx';write_workbook(p,include_reject=True)
    d=load_workbook(p)
    assert len(d['rejected_rows'])==1
    cmd=[sys.executable,'-m','adjudication.cli','run','--workbook',str(p),'--output-dir',str(tmp_path/'out'),'--as-at','2026-01-10T12:00:00+00:00']
    r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0,r.stderr
    out=tmp_path/'out'
    assert len(json.loads((out/'adjudication_report.json').read_text())['cases'])==2
    assert json.loads((out/'comparison_report.json').read_text())['comparisons'][0]['comparison_type']=='ADVISORY_ACTION_NOT_DISPOSITION_EQUIVALENT'
    assert (out/'rejected_rows.csv').exists()

def test_presentation_unverified_label_is_not_explicit_identity(event,data):
    from dataclasses import replace
    from adjudication.domain.models import Product,Study
    from adjudication.workflow.case_service import CaseService
    p=Product('SKU','Glucodyne SoloJet 100U','2-8','S','A',source_row=2)
    s=Study('S','Glucodyne SoloJet 100U',True,'ok','limit','A')
    c=CaseService({**data,'products':[p],'studies':[s]}).create_case(replace(event,raw={'tenant_code':'A'},product_ref='SKU'),event.alert_ts_utc)
    # No study-body or controlled product-ID attestation is supplied. Name-only is not scientific validation.
    assert any(g['gap_type']=='STUDY_RELATIONSHIP_UNVERIFIED' for g in c.gaps)
