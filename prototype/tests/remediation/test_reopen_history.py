from dataclasses import replace
from adjudication.workflow.case_service import CaseService
from adjudication.audit.event_store import audit_rows
from adjudication.reporting.report_builder import build_report

def test_reopen_keeps_parent_and_links_original_clock(event,data):
    s=CaseService(data);c=s.create_case(replace(event,readjudicated=True),event.alert_ts_utc)
    assert c.prior_case_id in s.all_attempts
    parent=s.all_attempts[c.prior_case_id]
    clocks=[x for x in parent.events if x.event_type=='REGULATORY_CLOCK_CALCULATED']
    assert len(clocks)==1
    linked=next(x for x in c.events if x.event_type=='REGULATORY_CLOCK_LINKED')
    assert linked.payload['original_clock_event_id']==clocks[0].event_id
    exported=build_report(list(s.all_attempts.values()),{},event.alert_ts_utc,'synthetic')
    assert len(exported['cases'])==2 and any(x['case_id']==parent.case_id for x in exported['cases'])

def test_all_real_reopened_parents_survive(workbook_data):
    s=CaseService(workbook_data)
    for e in workbook_data['events']:s.create_case(e,e.alert_ts_utc)
    assert len(s.all_attempts)==481
    reopened=[c for c in s.all_attempts.values() if c.prior_case_id]
    assert len(reopened)==61 and all(c.prior_case_id in s.all_attempts for c in reopened)
    assert sum(x.event_type=='REGULATORY_CLOCK_CALCULATED' for c in s.all_attempts.values() for x in c.events)==420

def test_reopen_same_parent_twice_never_overwrites_attempt(event,data):
    s=CaseService(data);parent=s.create_case(event,event.alert_ts_utc)
    a=s.reopen_case(parent,'first',event.alert_ts_utc)
    b=s.reopen_case(parent,'second',event.alert_ts_utc)
    assert a.case_id!=b.case_id and len(s.all_attempts)==3
    assert s.all_attempts[a.case_id] is a
