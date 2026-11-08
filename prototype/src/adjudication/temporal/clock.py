from __future__ import annotations
from datetime import datetime, timedelta, timezone
from ..domain.models import ExcursionEvent

def calculate_clock(event:ExcursionEvent,evaluated_at:datetime|None=None,default_window:float=72.0):
    evaluated_at=evaluated_at or datetime.now(timezone.utc)
    if evaluated_at.tzinfo is None: evaluated_at=evaluated_at.replace(tzinfo=timezone.utc)
    window=event.reg_window_hours if event.reg_window_hours is not None else default_window
    due=event.alert_ts_utc+timedelta(hours=window)
    elapsed=(evaluated_at-event.alert_ts_utc).total_seconds()/3600
    remaining=(due-evaluated_at).total_seconds()/3600
    if event.hours_to_notification is None:
        notified=None
        status="NOTIFICATION_STATUS_UNKNOWN" if remaining<0 else "OPEN"
    else:
        notified=event.hours_to_notification<=window
        if notified: status="NOTIFIED_WITHIN_WINDOW"
        elif remaining<0: status="OVERDUE_NOT_NOTIFIED"
        else: status="NOTIFIED_LATE"
    return {"alert_ts_utc":event.alert_ts_utc.isoformat(),"notification_due_at":due.isoformat(),"evaluated_at":evaluated_at.isoformat(),"hours_elapsed":round(elapsed,3),"hours_remaining":round(remaining,3),"status":status,"notified":notified,"is_breach":status in {"NOTIFIED_LATE","OVERDUE_NOT_NOTIFIED"}}
