from __future__ import annotations
import pandas as pd
from ..exceptions import WorkbookSchemaError

def norm(v): return str(v).strip().lower().replace(" ","_").replace("-","_")

def resolve_columns(df,aliases,sheet):
    available={norm(c):c for c in df.columns}; resolved={}; missing=[]
    for logical,candidates in aliases.items():
        for candidate in candidates:
            key=norm(candidate)
            if key in available: resolved[logical]=available[key]; break
        else: missing.append(logical)
    if missing: raise WorkbookSchemaError(f"Sheet '{sheet}' missing {missing}; available: {list(df.columns)}")
    return resolved

def clean(v):
    if v is None or (isinstance(v,float) and pd.isna(v)): return None
    s=str(v).strip(); return s or None

def to_utc(v):
    if v is None or (isinstance(v,float) and pd.isna(v)): return None
    dt=pd.to_datetime(v,utc=True,errors="coerce"); return None if pd.isna(dt) else dt.to_pydatetime()

def to_float(v):
    try: f=float(v)
    except (TypeError,ValueError): return None
    return None if pd.isna(f) else f

def to_bool(v): return isinstance(v,bool) and v or str(v).strip().lower() in {"true","yes","y","1","opened"}
