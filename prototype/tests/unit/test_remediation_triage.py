from adjudication.rules import engine

def test_parse_workbook_spelling_without_authorization():
    assert engine.parse_triage('NON_ACTIONABLE — duplicate of earlier alert')=='NON_ACTIONABLE'
    r=engine.evaluate('C',{'status':'NOT_APPLICABLE'},[],None,'NON_ACTIONABLE — duplicate',False)
    assert r['proposed_disposition']=='MANUAL_REVIEW' and not r['auto_close_authorized']

def test_historical_triage_never_hides_known_late():
    r=engine.evaluate('C',{'status':'NOTIFIED_LATE'},[{'gap_type':'CONFLICT'}],None,'NONACTIONABLE sensor artefact',True)
    assert r['notification_action']=='ESCALATE_REGULATORY_NOTIFICATION'
    assert r['proposed_disposition']!='NO_ACTION_REQUIRED'

def test_nonreportable_unknown_clock_does_not_invent_obligation():
    r=engine.evaluate('C',{'status':'NOT_APPLICABLE'},[],None,'ACTIONABLE',False)
    assert r['notification_action']=='NONE'
