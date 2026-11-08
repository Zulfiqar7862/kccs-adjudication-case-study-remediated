from datetime import datetime, timezone
from adjudication.workflow.case_service import CaseService

def test_case_creation_and_audit(event,data):
    service=CaseService(data)
    case=service.create_case(event,evaluated_at=datetime(2026,1,2,tzinfo=timezone.utc))
    assert case.case_id=="CASE-EVT-001" and case.recommendation
    assert any(e.event_type=="REGULATORY_CLOCK_CALCULATED" for e in case.events)

def test_reopen_generates_recommendation(event,data):
    event.readjudicated=True
    service=CaseService(data)
    case=service.create_case(event,evaluated_at=datetime(2026,1,2,tzinfo=timezone.utc))
    assert case.prior_case_id=="CASE-EVT-001" and case.reopen_count==1
    assert case.recommendation is not None
    assert any(e.event_type=="RECOMMENDATION_GENERATED" for e in case.events)
