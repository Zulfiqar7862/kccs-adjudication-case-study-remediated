from adjudication.rules.engine import evaluate

def test_nonactionable_triage():
    result=evaluate("C1",{"status":"OPEN","is_breach":False},[],None,"NONACTIONABLE duplicate of earlier alert",False)
    assert result["proposed_disposition"]=="MANUAL_REVIEW"

def test_confirmed_breach():
    result=evaluate("C1",{"status":"NOTIFIED_LATE","is_breach":True},[],None,"ACTIONABLE excursion confirmed",True)
    assert result["proposed_disposition"]=="ESCALATE_REGULATORY_NOTIFICATION"

def test_unknown_notification():
    result=evaluate("C1",{"status":"NOTIFICATION_STATUS_UNKNOWN","is_breach":False},[],None,"ACTIONABLE excursion confirmed",True)
    assert result["proposed_disposition"]=="ESCALATE_FOR_NOTIFICATION_REVIEW"

def test_gap_rule():
    result=evaluate("C1",{"status":"OPEN","is_breach":False},[{"gap_type":"X"}],None,"ACTIONABLE excursion confirmed",False)
    assert result["proposed_disposition"]=="MANUAL_REVIEW"
