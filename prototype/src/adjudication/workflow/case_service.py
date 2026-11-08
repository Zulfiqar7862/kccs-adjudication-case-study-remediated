from __future__ import annotations
import uuid
from datetime import datetime, timezone
from ..domain.models import Case, CaseEvent
from ..identity.resolver import IdentityResolver
from ..temporal.clock import calculate_clock
from ..temporal.effective_dating import select_effective
from ..evidence.gaps import evidence_gaps
from ..rules.engine import evaluate
from ..recommendations.assistant_stub import LLMRationaleService

class CaseService:
    def __init__(self,data,default_window=72.0):
        self.products=data["products"]; self.facilities=data["facilities"]; self.sops=data["sops"]; self.studies=data["studies"]
        self.resolver=IdentityResolver(data["aliases"]); self.overrides={o.event_id:o for o in data["overrides"]}
        self.default_window=default_window; self.llm=LLMRationaleService()
    def _event(self,case,etype,actor,new_state,payload,at):
        e=CaseEvent(str(uuid.uuid4()),case.case_id,etype,at,actor,case.state,new_state,payload); case.events.append(e); case.state=new_state; return e
    def _resolve_evidence(self,case,event,pres,fres,at):
        product=next((p for p in self.products if p.product_ref==pres["canonical"]),None)
        facility=next((f for f in self.facilities if f.facility_ref==fres["canonical"]),None)
        study=next((s for s in self.studies if product and s.study_ref==product.stability_study_ref),None)
        sop=select_effective(self.sops,event.alert_ts_utc)
        gaps=evidence_gaps(case.case_id,study,product.storage_spec_text if product else None)
        case.gaps.extend(gaps)
        return product,facility,study,sop,gaps
    def create_case(self,event,evaluated_at=None):
        at=evaluated_at or datetime.now(timezone.utc)
        case=Case(f"CASE-{event.event_id}",event.event_id,"DETECTED",at)
        self._event(case,"CASE_CREATED","system","TRIAGE",{"source_event_id":event.event_id},at)
        clock=calculate_clock(event,at,self.default_window)
        self._event(case,"REGULATORY_CLOCK_CALCULATED","regulatory_clock_service","EVIDENCE_COLLECTION",clock,at)
        pres=self.resolver.resolve(event.product_ref,"product",{p.product_ref for p in self.products})
        fres=self.resolver.resolve(event.facility_ref,"facility",{f.facility_ref for f in self.facilities})
        product,facility,study,sop,gaps=self._resolve_evidence(case,event,pres,fres,at)
        recommendation=evaluate(case.case_id,clock,gaps,study,event.triage_outcome,event.regulator_reportable)
        case.recommendation=recommendation
        rationale=self.llm.draft(recommendation,gaps)
        self._event(case,"RECOMMENDATION_GENERATED","deterministic_rules","PENDING_REVIEWER",{"recommendation":recommendation,"rationale":rationale,"product_resolution":pres,"facility_resolution":fres,"applicable_sop":sop.doc_id if sop else None},at)
        override=self.overrides.get(event.event_id)
        if override:
            case.override_reason=override.reason
            self._event(case,"REVIEWER_OVERRIDE_RECORDED","reviewer","UNDER_REVIEW",{"override_reason":override.reason},at)
        if event.disposition:
            case.disposition=event.disposition
            self._event(case,"DISPOSITION_RECORDED","reviewer","DISPOSITIONED",{"disposition":event.disposition},at)
        if event.readjudicated:
            case=self.reopen_case(case,"TT-CB-114 re-adjudication",at)
            clock=calculate_clock(event,at,self.default_window)
            pres=self.resolver.resolve(event.product_ref,"product",{p.product_ref for p in self.products})
            fres=self.resolver.resolve(event.facility_ref,"facility",{f.facility_ref for f in self.facilities})
            product,facility,study,sop,gaps=self._resolve_evidence(case,event,pres,fres,at)
            recommendation=evaluate(case.case_id,clock,gaps,study,event.triage_outcome,event.regulator_reportable)
            case.recommendation=recommendation
            rationale=self.llm.draft(recommendation,gaps)
            self._event(case,"RECOMMENDATION_GENERATED","deterministic_rules","PENDING_REVIEWER",{"recommendation":recommendation,"rationale":rationale,"product_resolution":pres,"facility_resolution":fres,"applicable_sop":sop.doc_id if sop else None},at)
        return case
    def reopen_case(self,case,reason,at=None):
        at=at or datetime.now(timezone.utc)
        reopened=Case(f"{case.case_id}-REOPEN-{case.reopen_count+1}",case.event_id,"REOPENED",at,case.reopen_count+1,case.case_id)
        self._event(reopened,"CASE_REOPENED","qa_or_platform","EVIDENCE_COLLECTION",{"reason":reason,"prior_case_id":case.case_id,"prior_state":case.state},at)
        return reopened
