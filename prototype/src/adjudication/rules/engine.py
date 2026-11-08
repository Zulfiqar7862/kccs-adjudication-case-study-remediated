from __future__ import annotations
RULES_VERSION="deterministic-rules-v1.1.0"

def evaluate(case_id,clock,gaps,study,triage_outcome=None,regulator_reportable=None):
    triage=(triage_outcome or "").upper()
    if "NONACTIONABLE" in triage or "AUTOCLOSE" in triage:
        return {"case_id":case_id,"proposed_disposition":"NO_ACTION_REQUIRED","rationale":"Source triage marked the alert non-actionable or auto-closed.","rules_version":RULES_VERSION,"confidence":0.85}
    if clock["status"] in {"NOTIFIED_LATE","OVERDUE_NOT_NOTIFIED"}:
        return {"case_id":case_id,"proposed_disposition":"ESCALATE_REGULATORY_NOTIFICATION","rationale":"Regulatory notification clock is breached or notification is late.","rules_version":RULES_VERSION,"confidence":0.95}
    if clock["status"]=="NOTIFICATION_STATUS_UNKNOWN":
        return {"case_id":case_id,"proposed_disposition":"ESCALATE_FOR_NOTIFICATION_REVIEW","rationale":"The notification window has passed, but notification evidence is unavailable.","rules_version":RULES_VERSION,"confidence":0.80}
    if gaps:
        return {"case_id":case_id,"proposed_disposition":"MANUAL_REVIEW","rationale":"Required evidence is incomplete or unreadable.","rules_version":RULES_VERSION,"confidence":0.70}
    if study and study.permitted_excursion_text:
        return {"case_id":case_id,"proposed_disposition":"REVIEW_EXCURSION_AGAINST_PERMITTED_LIMIT","rationale":"Readable stability evidence provides a permitted-excursion reference.","rules_version":RULES_VERSION,"confidence":0.80}
    return {"case_id":case_id,"proposed_disposition":"MANUAL_REVIEW","rationale":"No permitted-excursion reference available.","rules_version":RULES_VERSION,"confidence":0.65}
