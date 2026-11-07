from datetime import datetime, timezone
from adjudication.workflow.case_service import CaseService

def test_case_creation_and_audit(event,data):
    service=CaseService(data)
    case=service.create_case(event,evaluated_at=datetime(2026,1,2,tzinfo=timezone.utc))
    assert case.case_id=="CASE-EVT-001" and case.recommendation
    assert any(e.event_type=="REGULATORY_CLOCK_CALCULATED" for e in case.events)

def test_reopen_preserves_link(event,data):
    service=CaseService(data); original=service.create_case(event,evaluated_at=datetime(2026,1,2,tzinfo=timezone.utc))
    reopened=service.reopen_case(original,"New evidence",datetime(2026,6,1,tzinfo=timezone.utc))
    assert reopened.prior_case_id==original.case_id and reopened.reopen_count==1
