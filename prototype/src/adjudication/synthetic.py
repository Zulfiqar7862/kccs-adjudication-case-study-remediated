"""Explicit synthetic CI fixture, never a substitute for confidential qualification."""
from pathlib import Path
import pandas as pd

def write_workbook(path,include_reject=False):
    from .cli import EVENT_ALIASES,QUEUE_ALIASES,PRODUCT_ALIASES,FACILITY_ALIASES,SOP_ALIASES,STUDY_ALIASES,ALIAS_ALIASES,OVERRIDE_ALIASES
    tables={}
    mappings={'01_Excursion_Events':EVENT_ALIASES,'08_Reviewer_Queue_Log':QUEUE_ALIASES,'02_Product_Master':PRODUCT_ALIASES,'03_Facility_Registry':FACILITY_ALIASES,'05_SOP_Index':SOP_ALIASES,'06_Stability_Index':STUDY_ALIASES,'07_Alias_Observations':ALIAS_ALIASES,'09_Override_Reasons':OVERRIDE_ALIASES}
    for sheet,aliases in mappings.items():tables[sheet]=pd.DataFrame(columns=[v[0] for v in aliases.values()])
    events=[]
    for i in range(2):
        row={v[0]:None for v in EVENT_ALIASES.values()};row.update(event_id=f'SYNTHETIC-{i}',alert_ts_utc='2026-01-02T12:00:00+00:00',excursion_start_utc='2026-01-02T11:50:00+00:00',product_ref_as_received='SYNTHETIC-SKU',origin_ref_as_received='SYNTHETIC-FACILITY',regulator_reportable='Y' if i else 'N',reg_window_hours=72 if i else None,hours_to_notification=10 if i else None,case_opened='Y',reopened_later='N',triage_outcome='ACTIONABLE',tenant_code='SYNTHETIC-TENANT')
        events.append(row)
    if include_reject:events.append({**events[0],'event_id':None})
    tables['01_Excursion_Events']=pd.DataFrame(events)
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with pd.ExcelWriter(path) as writer:
        for sheet,df in tables.items():df.to_excel(writer,sheet_name=sheet,index=False)
    return path

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('path');args=p.parse_args();write_workbook(args.path)
