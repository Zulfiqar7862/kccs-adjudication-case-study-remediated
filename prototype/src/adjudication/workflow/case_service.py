from __future__ import annotations
import uuid
from datetime import datetime, timezone
from ..domain.models import Case, CaseEvent
from ..identity.resolver import IdentityResolver
from ..temporal.clock import calculate_clock
from ..temporal.effective_dating import select_effective, resolve_sops
from ..evidence.gaps import evidence_gaps
from ..rules.engine import evaluate
from ..recommendations.assistant_stub import LLMRationaleService

class CaseService:
    def __init__(self,data,default_window=72.0):
        self.products=data["products"]; self.facilities=data["facilities"]; self.sops=data["sops"]; self.studies=data["studies"]
        self.resolver=IdentityResolver(data["aliases"]); self.overrides={o.event_id:o for o in data["overrides"]}
        self.default_window=default_window; self.llm=LLMRationaleService()
        self.all_attempts={}
    def _event(self,case,etype,actor,new_state,payload,at):
        e=CaseEvent(str(uuid.uuid4()),case.case_id,etype,at,actor,case.state,new_state,payload); case.events.append(e); case.state=new_state; return e
    def resolve_product(self,event):
        tenant=event.raw.get('tenant_code'); value=(event.product_ref or '').strip().casefold()
        candidates=[p for p in self.products if tenant and p.tenant_code==tenant and value in {v.strip().casefold() for v in p.all_identifiers}]
        observations=self.resolver.observations(event.product_ref,'product')
        proposed=[]
        if not candidates:
            names={v.casefold() for a in observations if a.same for v in (a.alias_value,a.canonical_value)}
            proposed=[p for p in self.products if tenant and p.tenant_code==tenant and names.intersection(v.casefold() for v in p.all_identifiers)]
        return {'source':event.product_ref,'canonical':candidates[0].key if len(candidates)==1 else None,'tenant_code':tenant,'method':'tenant_exact_identifier' if len(candidates)==1 else 'candidate_requires_human_confirmation' if proposed else 'unresolved_or_conflict','confidence':None,'candidates':[p.key for p in candidates+proposed],'provenance':self.resolver.provenance(observations)}
    def _resolve_evidence(self,case,event,pres,fres,at):
        from ..evidence.eligibility import study_eligibility
        product=next((p for p in self.products if p.key==pres['canonical'] and p.tenant_code==event.raw.get('tenant_code')),None)
        facility=next((f for f in self.facilities if f.facility_ref==fres['canonical']),None)
        study,eligibility=study_eligibility(product,self.studies,event.raw.get('tenant_code'))
        case.study_eligibility=eligibility
        scope_date=event.excursion_start_utc or event.alert_ts_utc
        case.sop_resolution=resolve_sops(self.sops,event.raw.get('tenant_code'),scope_date,event.facility_ref,event.raw.get('dest_ref_as_received'))
        sop=None  # No metadata-only limit is asserted as governing authority.
        gaps=evidence_gaps(case.case_id,study,product.storage_spec_text if product else None)
        for issue in eligibility['issues']+case.sop_resolution['issues']:gaps.append({'case_id':case.case_id,'gap_type':issue,'severity':'high','detail':'Source study pointer is not eligible; human evidence resolution required.'})
        case.gaps.extend(gaps)
        return product,facility,study,sop,gaps
    def create_case(self,event,evaluated_at=None):
        at=evaluated_at or datetime.now(timezone.utc)
        case=Case(f"CASE-{event.event_id}",event.event_id,"DETECTED",at)
        self._event(case,"CASE_CREATED","system","TRIAGE",{"source_event_id":event.event_id},at)
        clock=calculate_clock(event,at,self.default_window)
        self._event(case,"REGULATORY_CLOCK_CALCULATED","regulatory_clock_service","EVIDENCE_COLLECTION",clock,at)
        pres=self.resolve_product(event)
        fres=self.resolver.resolve(event.facility_ref,"facility",{f.facility_ref for f in self.facilities})
        product,facility,study,sop,gaps=self._resolve_evidence(case,event,pres,fres,at)
        recommendation=evaluate(case.case_id,clock,gaps,study,event.triage_outcome,event.regulator_reportable)
        case.recommendation=recommendation
        rationale=self.llm.draft(recommendation,gaps)
        self._event(case,"RECOMMENDATION_GENERATED","deterministic_rules","PENDING_REVIEWER",{"recommendation":recommendation,"rationale":rationale,"product_resolution":pres,"facility_resolution":fres,"applicable_sop":sop.doc_id if sop else None,"study_eligibility":case.study_eligibility,"sop_resolution":case.sop_resolution},at)
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
            pres=self.resolve_product(event)
            fres=self.resolver.resolve(event.facility_ref,"facility",{f.facility_ref for f in self.facilities})
            product,facility,study,sop,gaps=self._resolve_evidence(case,event,pres,fres,at)
            recommendation=evaluate(case.case_id,clock,gaps,study,event.triage_outcome,event.regulator_reportable)
            case.recommendation=recommendation
            rationale=self.llm.draft(recommendation,gaps)
            self._event(case,"RECOMMENDATION_GENERATED","deterministic_rules","PENDING_REVIEWER",{"recommendation":recommendation,"rationale":rationale,"product_resolution":pres,"facility_resolution":fres,"applicable_sop":sop.doc_id if sop else None,"study_eligibility":case.study_eligibility,"sop_resolution":case.sop_resolution},at)
        return case
    def reopen_case(self,case,reason,at=None):
        at=at or datetime.now(timezone.utc)
        reopened=Case(f"{case.case_id}-REOPEN-{case.reopen_count+1}",case.event_id,"REOPENED",at,case.reopen_count+1,case.case_id)
        self._event(reopened,"CASE_REOPENED","qa_or_platform","EVIDENCE_COLLECTION",{"reason":reason,"prior_case_id":case.case_id,"prior_state":case.state},at)
        return reopened
