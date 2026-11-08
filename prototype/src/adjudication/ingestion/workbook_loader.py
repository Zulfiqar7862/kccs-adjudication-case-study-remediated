from __future__ import annotations
import pandas as pd
from math import isfinite
from datetime import datetime,timezone,timedelta
from ..exceptions import WorkbookSchemaError

def norm(v): return str(v).strip().lower().replace(" ","_").replace("-","_")

def resolve_columns(df,aliases,sheet,optional=()):
    available={norm(c):c for c in df.columns}; resolved={}; missing=[]
    for logical,candidates in aliases.items():
        for candidate in candidates:
            key=norm(candidate)
            if key in available: resolved[logical]=available[key]; break
        else:
            if logical not in optional: missing.append(logical)
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
    return f if isfinite(f) else None

def to_bool(v):
    value=str(v).strip().casefold()
    if value in {'true','yes','y','1','opened'}:return True
    if value in {'false','no','n','0'}:return False
    return None

def to_offset_hours(v):
    value=clean(v)
    if value is None:return None
    try:
        if ':' not in value:return to_float(value)
        sign=-1 if value.startswith('-') else 1
        hours,minutes=map(int,value.lstrip('+-').split(':'))
        if hours>14 or minutes>=60:return None
        return sign*(hours+minutes/60)
    except ValueError:return None

def local_to_utc(value,offset):
    value=clean(value)
    if not value or offset is None:return None
    try:return datetime.fromisoformat(value).replace(tzinfo=timezone(timedelta(hours=offset))).astimezone(timezone.utc).isoformat()
    except ValueError:return None
