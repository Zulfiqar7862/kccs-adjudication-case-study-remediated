from adjudication.audit.event_store import audit_rows

def test_audit_rows(event,data):
    from adjudication.workflow.case_service import CaseService
    service=CaseService(data); case=service.create_case(event)
    rows=audit_rows([case])
    assert len(rows)>=2 and all(r["case_id"]==case.case_id for r in rows)
