from adjudication.rules.engine import evaluate

def test_breach_rule():
    result=evaluate("C1",{"is_breach":True},[],None)
    assert result["proposed_disposition"]=="ESCALATE_REGULATORY_NOTIFICATION"

def test_gap_rule():
    result=evaluate("C1",{"is_breach":False},[{"gap_type":"X"}],None)
    assert result["proposed_disposition"]=="MANUAL_REVIEW"
