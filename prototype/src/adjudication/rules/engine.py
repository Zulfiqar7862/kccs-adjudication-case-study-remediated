from __future__ import annotations
RULES_VERSION="deterministic-rules-v1.0.0"

def evaluate(case_id,clock,gaps,study):
    if clock["is_breach"]: return {"case_id":case_id,"proposed_disposition":"ESCALATE_REGULATORY_NOTIFICATION","rationale":"Regulatory notification clock is breached or notification is late.","rules_version":RULES_VERSION,"confidence":0.95}
    if gaps: return {"case_id":case_id,"proposed_disposition":"MANUAL_REVIEW","rationale":"Required evidence is incomplete or unreadable.","rules_version":RULES_VERSION,"confidence":0.70}
    if study and study.permitted_excursion_text: return {"case_id":case_id,"proposed_disposition":"REVIEW_EXCURSION_AGAINST_PERMITTED_LIMIT","rationale":"Readable stability evidence provides a permitted-excursion reference.","rules_version":RULES_VERSION,"confidence":0.80}
    return {"case_id":case_id,"proposed_disposition":"MANUAL_REVIEW","rationale":"No permitted-excursion reference available.","rules_version":RULES_VERSION,"confidence":0.65}
