from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

@dataclass
class ExcursionEvent:
    event_id:str; alert_ts_utc:datetime; excursion_start_utc:datetime|None
    product_ref:str|None; facility_ref:str|None; temperature:float|None
    reg_window_hours:float|None; hours_to_notification:float|None
    recommendation:str|None; disposition:str|None; case_opened:bool; readjudicated:bool
    triage_outcome:str|None=None; regulator_reportable:bool|None=None; reviewer_overrode:bool|None=None
    raw:dict=field(default_factory=dict)

@dataclass
class Product:
    product_ref:str; product_name:str|None; storage_spec_text:str|None; stability_study_ref:str|None; tenant_code:str|None
    identifiers:tuple[str,...]=()
    source_row:int|None=None
    @property
    def key(self): return f"{self.tenant_code}|product|{self.source_row or self.product_ref}"
    @property
    def all_identifiers(self): return tuple(v for v in (self.product_ref,self.product_name,*self.identifiers) if v)

@dataclass
class Facility:
    facility_ref:str; facility_name:str|None; timezone:str|None; tenant_code:str|None

@dataclass
class SOP:
    doc_id:str; revision:str|None; effective_from:datetime|None; effective_to:datetime|None; supersedes_text:str|None

@dataclass
class Study:
    study_ref:str; product_ref:str|None; readable:bool; outcome:str|None; permitted_excursion_text:str|None; tenant_code:str|None
    study_type:str|None=None
    source_row:int|None=None

@dataclass
class Alias:
    alias_value:str; canonical_value:str; entity_type:str|None
    same:bool=True
    confirmed_by:str|None=None
    confirmed_on:str|None=None
    comment:str|None=None
    source_row:int|None=None

@dataclass
class Override:
    event_id:str; reason:str

@dataclass
class CaseEvent:
    event_id:str; case_id:str; event_type:str; occurred_at:datetime; actor:str; previous_state:str|None; new_state:str; payload:dict=field(default_factory=dict)

@dataclass
class Case:
    case_id:str; event_id:str; state:str; opened_at:datetime; reopen_count:int=0; prior_case_id:str|None=None
    events:list[CaseEvent]=field(default_factory=list); gaps:list[dict]=field(default_factory=list)
    recommendation:dict|None=None; disposition:str|None=None; override_reason:str|None=None
