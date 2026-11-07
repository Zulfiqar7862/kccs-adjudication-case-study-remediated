from __future__ import annotations
from datetime import datetime
from ..domain.models import SOP

def select_effective(sops,as_at:datetime,doc_id:str|None=None):
    candidates=[s for s in sops if (doc_id is None or s.doc_id==doc_id) and s.effective_from and s.effective_from<=as_at and (s.effective_to is None or s.effective_to>as_at)]
    return max(candidates,key=lambda s:s.effective_from) if candidates else None
