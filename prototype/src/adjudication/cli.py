from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
from .ingestion.workbook_loader import resolve_columns, clean, to_utc, to_float, to_bool, to_offset_hours, local_to_utc, WorkbookSchemaError
from .domain.models import ExcursionEvent, Product, Facility, SOP, Study, Alias, Override
from .workflow.case_service import CaseService
from .audit.event_store import audit_rows
from .reporting.report_builder import build_report

EVENT_ALIASES={"event_id":["event_id","alert_id","excursion_id","case_id","record_id"],"alert_ts_utc":["alert_ts_utc","alert_timestamp_utc","alert_time_utc","alert_ts"],"excursion_start_utc":["excursion_start_utc","excursion_start"],"product_ref":["product_ref_as_received","product_ref","product"],"facility_ref":["origin_ref_as_received","facility_ref_as_received","facility_ref","dest_ref_as_received","site_ref","location"],"temperature":["mean_temp_c","observed_temperature_c","temperature_c","temperature"],"reg_window_hours":["reg_window_hours","regulatory_window_hours","notification_window_hours"],"hours_to_notification":["hours_to_notification","hours_to_notify"],"recommendation":["rules_engine_recommendation","recommendation","assistant_recommendation"],"disposition":["final_disposition","disposition","reviewer_disposition"],"case_opened":["case_opened","case_opened_flag"],"readjudicated":["reopened_later","readjudicated","re_adjudicated","readjudication_flag"],"triage_outcome":["triage_outcome"],"regulator_reportable":["regulator_reportable"],"reviewer_overrode":["reviewer_overrode"]}
QUEUE_ALIASES={"event_id":["case_ref","event_id","alert_id","case_id","excursion_id"],"reviewer":["reviewer_id","reviewer","reviewer_name"],"local_start":["local_start","review_start_local","start_local"],"local_end":["local_end","review_end_local","end_local"],"utc_offset":["reviewer_utc_offset","utc_offset","offset_hours"],"minutes":["active_minutes","minutes","review_minutes","duration_minutes"],"queue_wait_hours":["queue_wait_hours","wait_hours"]}
PRODUCT_ALIASES={"product_ref":["internal_sku","product_ref","product_id","sku","product_code","gtin","legacy_code"],"product_name":["brand_as_labelled","product_name","product","generic_inn","name"],"storage_spec_text":["storage_spec_text","storage_specification","storage_condition","spec_text"],"stability_study_ref":["stability_study_ref","stability_study_id","stability_ref"],"tenant_code":["tenant_code","tenant","tenant_id"]}
FACILITY_ALIASES={"facility_ref":["code_in_source","record_id","facility_ref","facility_id","site_id","site_ref"],"facility_name":["name_in_source","facility_name","site_name","name"],"timezone":["timezone_in_source","timezone","tz","time_zone"],"tenant_code":["tenant_code","tenant","tenant_id"]}
SOP_ALIASES={"doc_id":["doc_id","sop_id","document_id"],"revision":["revision","revision_id","version"],"effective_from":["effective_from","effective_date","valid_from"],"effective_to":["effective_to","end_date","valid_to"],"supersedes_text":["supersedes_text","supersedes","supersedes_revision"]}
STUDY_ALIASES={"study_ref":["study_ref","study_id","stability_study_ref"],"product_ref":["product_text_as_written","product_ref","product_id","sku"],"readable":["readable","is_readable","document_readable"],"outcome":["outcome_text","outcome","study_outcome","result"],"permitted_excursion_text":["permitted_excursion_text","permitted_excursion","excursion_limit"],"tenant_code":["tenant_code","tenant","tenant_id"]}
ALIAS_ALIASES={"entity_kind":["entity_kind","entity_type","type","entity"],"string_a":["string_a","canonical_value","canonical"],"string_b":["string_b","alias_value","alias"],"same":["same_real_world_thing","same","confirmed"]}
OVERRIDE_ALIASES={"event_id":["case_ref","event_id","alert_id","case_id","excursion_id"],"reason":["verbatim_reason","reason","override_reason","reason_text"]}

def load_workbook(path):
    path=Path(path)
    if not path.exists(): raise FileNotFoundError(f"Workbook not found: {path}")
    def sheet(name):
        try: return pd.read_excel(path,sheet_name=name)
        except ValueError as e: raise WorkbookSchemaError(f"Cannot read required sheet '{name}': {e}")
    events=[]; rejected=[]
    df=sheet("01_Excursion_Events"); c=resolve_columns(df,EVENT_ALIASES,"01_Excursion_Events")
    ids=df[c['event_id']].map(clean)
    duplicates=set(ids[ids.duplicated(keep=False)].dropna())
    for _,r in df.iterrows():
        eid=clean(r[c["event_id"]]); alert=to_utc(r[c["alert_ts_utc"]])
        if not eid or not alert or eid in duplicates:
            rejected.append({'sheet':'01_Excursion_Events','source_row':int(r.name)+2,'reason':'duplicate_id' if eid in duplicates else 'missing_id_or_invalid_alert','event_id':eid});continue
        events.append(ExcursionEvent(eid,alert,to_utc(r[c["excursion_start_utc"]]),clean(r[c["product_ref"]]),clean(r[c["facility_ref"]]),to_float(r[c["temperature"]]),to_float(r[c["reg_window_hours"]]),to_float(r[c["hours_to_notification"]]),clean(r[c["recommendation"]]),clean(r[c["disposition"]]),to_bool(r[c["case_opened"]]),to_bool(r[c["readjudicated"]]),clean(r[c["triage_outcome"]]),to_bool(r[c["regulator_reportable"]]),to_bool(r[c["reviewer_overrode"]]),{k:(None if pd.isna(v) else v) for k,v in r.to_dict().items()}))
    if not events: raise WorkbookSchemaError("No usable excursion events were loaded.")
    def records(name,aliases,builder,optional=()):
        df=sheet(name); c=resolve_columns(df,aliases,name,optional); out=[]
        for _,r in df.iterrows():
            item=builder(r,c)
            if item: out.append(item)
        return out
    def opt(r,c,k): return clean(r[c[k]]) if k in c else None
    queue=records("08_Reviewer_Queue_Log",QUEUE_ALIASES,lambda r,c:{"event_id":clean(r[c["event_id"]]),"reviewer":clean(r[c["reviewer"]]),"local_start":clean(r[c["local_start"]]),"local_end":clean(r[c["local_end"]]),"utc_offset":to_offset_hours(r[c["utc_offset"]]),"utc_start":local_to_utc(r[c["local_start"]],to_offset_hours(r[c["utc_offset"]])),"utc_end":local_to_utc(r[c["local_end"]],to_offset_hours(r[c["utc_offset"]])),"minutes":to_float(r[c["minutes"]]),"queue_wait_hours":to_float(r[c["queue_wait_hours"]])} if clean(r[c["event_id"]]) else None)
    products=records("02_Product_Master",PRODUCT_ALIASES,lambda r,c:Product(next((clean(r.get(k)) for k in ('internal_sku','gtin','legacy_code','brand_as_labelled') if clean(r.get(k))),f"ROW-{r.name+2}"),clean(r[c["product_name"]]),clean(r[c["storage_spec_text"]]),clean(r[c["stability_study_ref"]]),opt(r,c,"tenant_code"),tuple(clean(r.get(k)) for k in ('internal_sku','gtin','legacy_code','brand_as_labelled') if clean(r.get(k))),int(r.name)+2),optional=("tenant_code",))
    facilities=records("03_Facility_Registry",FACILITY_ALIASES,lambda r,c:Facility(clean(r[c["facility_ref"]]),clean(r[c["facility_name"]]),clean(r[c["timezone"]]),opt(r,c,"tenant_code")) if clean(r[c["facility_ref"]]) else None,optional=("tenant_code",))
    sops=records("05_SOP_Index",SOP_ALIASES,lambda r,c:SOP(clean(r[c["doc_id"]]),clean(r[c["revision"]]),to_utc(r[c["effective_from"]]),to_utc(r[c["effective_to"]]),clean(r[c["supersedes_text"]]),clean(r.get("tenant_code")),clean(r.get("title")),clean(r.get("applies_to_facilities_text")),clean(r.get("acceptance_limits_location")),int(r.name)+2) if clean(r[c["doc_id"]]) else None)
    studies=records("06_Stability_Index",STUDY_ALIASES,lambda r,c:Study(clean(r[c["study_ref"]]),clean(r[c["product_ref"]]),to_bool(r[c["readable"]]),clean(r[c["outcome"]]),clean(r[c["permitted_excursion_text"]]),opt(r,c,"tenant_code"),clean(r.get("study_type")),int(r.name)+2) if clean(r[c["study_ref"]]) else None,optional=("tenant_code",))
    aliases=records("07_Alias_Observations",ALIAS_ALIASES,lambda r,c:Alias(clean(r[c["string_b"]]),clean(r[c["string_a"]]),(clean(r[c["entity_kind"]]) or "any").lower(),to_bool(r[c["same"]]),clean(r.get("confirmed_by")),clean(r.get("confirmed_on")),clean(r.get("comment")),int(r.name)+2) if clean(r[c["string_a"]]) and clean(r[c["string_b"]]) else None)
    overrides=records("09_Override_Reasons",OVERRIDE_ALIASES,lambda r,c:Override(clean(r[c["event_id"]]),clean(r[c["reason"]])) if clean(r[c["event_id"]]) and clean(r[c["reason"]]) else None)
    return {"rejected_rows":rejected,"events":events,"reviewer_queue":queue,"products":products,"facilities":facilities,"sops":sops,"studies":studies,"aliases":aliases,"overrides":overrides}

def run(workbook,output_dir="output",as_at=None):
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    data=load_workbook(workbook); service=CaseService(data)
    evaluated_at=datetime.fromisoformat(as_at) if isinstance(as_at,str) else as_at or datetime.now(timezone.utc)
    if evaluated_at.tzinfo is None: raise ValueError("--as-at requires an explicit UTC offset")
    for e in data["events"]: service.create_case(e,evaluated_at)
    cases=list(service.all_attempts.values())
    summary=[]; gaps=[]
    for case in cases:
        clock_event=next((e for e in case.events if e.event_type in {"REGULATORY_CLOCK_CALCULATED","REGULATORY_CLOCK_LINKED"}),None)
        clock_payload=clock_event.payload.get("original_clock",clock_event.payload) if clock_event else {}
        summary.append({"case_id":case.case_id,"event_id":case.event_id,"state":case.state,"historical_disposition":case.disposition,"recommendation":case.recommendation["proposed_disposition"] if case.recommendation else None,"confidence":case.recommendation["confidence"] if case.recommendation else None,"override_reason":case.override_reason,"reopen_count":case.reopen_count,"prior_case_id":case.prior_case_id,"notification_status":clock_payload.get("status"),"notification_due_at":clock_payload.get("notification_due_at"),"evidence_gap_count":len(case.gaps)})
        gaps.extend(case.gaps)
    counts={"excursion_events":len(data["events"]),"cases":len(cases),"reviewer_queue_records":len(data["reviewer_queue"]),"products":len(data["products"]),"facilities":len(data["facilities"]),"sop_revisions":len(data["sops"]),"stability_studies":len(data["studies"]),"alias_observations":len(data["aliases"]),"positive_alias_observations":sum(a.same is True for a in data["aliases"]),"rejected_event_rows":len(data["rejected_rows"]),"override_reasons":len(data["overrides"])}
    report=build_report(cases,counts,evaluated_at,workbook)
    pd.DataFrame(data['rejected_rows'],columns=['sheet','source_row','reason','event_id']).to_csv(out/'rejected_rows.csv',index=False)
    comparisons=[]
    for e in data['events']:
        c=next(c for c in cases if c.event_id==e.event_id and not c.prior_case_id)
        comparisons.append({'event_id':e.event_id,'historical_assistant_draft':e.recommendation,'historical_disposition':e.disposition,'new_advisory_action':c.recommendation['proposed_disposition'],'comparison_type':'ADVISORY_ACTION_NOT_DISPOSITION_EQUIVALENT','disposition_difference':'NOT_EVALUATED_NO_NEW_DISPOSITION','reason':c.recommendation['rationale'],'gap_types':sorted({g['gap_type'] for g in c.gaps}),'reopened_source_flag':e.readjudicated})
    (out/'comparison_report.json').write_text(json.dumps({'comparisons':comparisons,'qualification':'Explained advisory replay, NOT a qualified counterfactual disposition evaluation.'},indent=2),encoding='utf-8')
    (out/"adjudication_report.json").write_text(json.dumps(report,indent=2,default=str),encoding="utf-8")
    pd.DataFrame(summary).to_csv(out/"adjudication_summary.csv",index=False)
    pd.DataFrame(audit_rows(cases)).to_csv(out/"case_audit_log.csv",index=False)
    pd.DataFrame(gaps).to_csv(out/"evidence_gaps.csv",index=False)
    from hashlib import sha256
    import subprocess
    from .rules.engine import RULES_VERSION
    root=Path(__file__).resolve().parents[3]
    try:
        commit=subprocess.run(["git","-C",str(root),"rev-parse","HEAD"],capture_output=True,text=True,check=False)
    except FileNotFoundError:
        commit=subprocess.CompletedProcess([],1,stdout="",stderr="git not installed")
    digest=sha256(Path(workbook).read_bytes()).hexdigest()
    manifest={"schema_version":"2.0","as_at":evaluated_at.isoformat(),"workbook_sha256":digest,"code_commit":commit.stdout.strip() if commit.returncode==0 else None,"code_commit_status":"git_checkout" if commit.returncode==0 else "archive_no_git_metadata","rules_version":RULES_VERSION,"reference_bundle":{"workbook_sha256":digest,"policy_version":"brief-pack-v1","alias_policy":"one-hop-candidates-v2","sop_policy":"conflicts-abstain-v2"},"audit_semantics":"defensive mutable-file export; no immutable retention guarantee","record_counts":counts}
    (out/"run_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(f"Processed {len(cases)} cases from {len(data['events'])} excursion events.")
    print(f"Outputs written to: {out.resolve()}")
    return 0

def main():
    p=argparse.ArgumentParser(description="KCCS excursion adjudication prototype")
    sub=p.add_subparsers(dest="command",required=True)
    r=sub.add_parser("run"); r.add_argument("--workbook",required=True); r.add_argument("--output-dir",default="output"); r.add_argument("--as-at",help="Fixed timezone-aware replay instant")
    a=p.parse_args()
    return run(a.workbook,a.output_dir,a.as_at) if a.command=="run" else 1

if __name__=="__main__": raise SystemExit(main())
