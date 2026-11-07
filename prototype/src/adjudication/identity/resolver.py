from __future__ import annotations
from typing import Iterable
from ..domain.models import Alias

class IdentityResolver:
    def __init__(self,aliases:Iterable[Alias]):
        self.map={}
        for a in aliases: self.map[((a.entity_type or "any").lower(),a.alias_value.strip().lower())]=a.canonical_value
    def resolve(self,value,entity_type,known):
        if not value: return {"source":None,"canonical":None,"method":"missing","confidence":0.0}
        if value.strip().lower() in {v.lower() for v in known}: return {"source":value,"canonical":value,"method":"exact_source_match","confidence":1.0}
        for etype in (entity_type,"any"):
            canonical=self.map.get((etype,value.strip().lower()))
            if canonical: return {"source":value,"canonical":canonical,"method":"confirmed_alias","confidence":0.9 if etype==entity_type else 0.75}
        return {"source":value,"canonical":None,"method":"unresolved","confidence":0.0}
