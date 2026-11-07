from datetime import datetime, timezone
from adjudication.workflow.case_service import CaseService

def test_reopen(event,data):
    service=CaseService(data); original=service.create_case(event,evaluated_at=datetime(2026,1,2,tzinfo=timezone.utc))
    reopened=service.reopen_case(original,"TT-CB-114")
    assert reopened.prior_case_id==original.case_id
