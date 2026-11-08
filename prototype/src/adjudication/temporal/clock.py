"""Offline notification assessment. No inference from tenant name or default window."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone, time, date
from math import isfinite
from zoneinfo import ZoneInfo

@dataclass(frozen=True)
class NotificationPolicy:
    policy_id: str
    kind: str = 'hours'
    hours: float | None = None
    timezone: str | None = None
    calendar_id: str | None = None
    holidays: tuple[str, ...] | None = None
    cutoff: str | None = None
    version: str = 'brief-pack-v1'

def resolve_policy(event):
    # Supplied row window is retained as an EXTRACTED historical policy claim,
    # not a legal opinion or a conversion of next-business-day to 24 hours.
    if event.reg_window_hours is not None:
        return NotificationPolicy('extract:reg_window_hours','extracted_hours',event.reg_window_hours)
    jurisdiction=event.raw.get('jurisdiction')
    facts={'BR':120, 'IN_NOTIFIABLE':360, 'EU_72H_MARKET_CONFIRMED':72}
    if jurisdiction in facts:
        return NotificationPolicy(jurisdiction,'hours',facts[jurisdiction])
    return None  # US state/calendar/cutoff and unlisted jurisdictions unknown.

def policy_due(alert,policy):
    if not policy:return None
    if policy.kind in {'hours','extracted_hours'}:
        if policy.hours is None or not isfinite(policy.hours) or policy.hours<=0:return None
        return alert+timedelta(hours=policy.hours)
    if policy.kind=='next_business_day':
        if not all([policy.timezone,policy.calendar_id,policy.cutoff]) or policy.holidays is None:return None
        local=alert.astimezone(ZoneInfo(policy.timezone));day=local.date()+timedelta(days=1)
        holidays={date.fromisoformat(h) for h in policy.holidays}
        while day.weekday()>=5 or day in holidays:day+=timedelta(days=1)
        h,m=map(int,policy.cutoff.split(':'))
        return datetime.combine(day,time(h,m),ZoneInfo(policy.timezone)).astimezone(timezone.utc)
    return None

def calculate_clock(event,evaluated_at=None,default_window=None,policy=None):
    at=evaluated_at or datetime.now(timezone.utc)
    if at.tzinfo is None:raise ValueError('evaluated_at must be timezone-aware')
    applicability='REPORTABLE' if event.regulator_reportable is True else ('NOT_REPORTABLE' if event.regulator_reportable is False else 'UNKNOWN')
    result={'alert_ts_utc':event.alert_ts_utc.isoformat(),'evaluated_at':at.isoformat(),'applicability':applicability,'policy_status':'NOT_RESOLVED','policy_id':None,'policy_version':None,'notification_evidence':'UNKNOWN','notification_due_at':None,'status':'APPLICABILITY_UNKNOWN','notified':None,'is_breach':False,'hours_elapsed':round((at-event.alert_ts_utc).total_seconds()/3600,3),'hours_remaining':None}
    if applicability=='NOT_REPORTABLE':
        result['status']='INPUT_CONFLICT' if event.hours_to_notification is not None else 'NOT_APPLICABLE'
        return result
    if applicability=='UNKNOWN':return result
    policy=policy or resolve_policy(event)
    due=policy_due(event.alert_ts_utc,policy)
    if due is None:result['status']='POLICY_UNKNOWN';return result
    result.update(policy_status='EXTRACTED_WINDOW_UNQUALIFIED' if policy.kind=='extracted_hours' else 'RESOLVED',policy_id=policy.policy_id,policy_version=policy.version,notification_due_at=due.isoformat(),hours_remaining=round((due-at).total_seconds()/3600,3))
    hours=event.hours_to_notification
    if hours is not None:
        if not isfinite(hours) or hours<0:result['status']='INPUT_CONFLICT';return result
        receipt=event.alert_ts_utc+timedelta(hours=hours)
        if receipt>at:result.update(notification_evidence='NOT_YET_OBSERVED',status='OPEN' if at<=due else 'NOTIFICATION_STATUS_UNKNOWN');return result
        late=receipt>due
        result.update(notification_evidence='EXTRACTED_RECEIPT',notified=not late,status='NOTIFIED_LATE' if late else 'NOTIFIED_WITHIN_WINDOW',is_breach=late)
    elif event.raw.get('notification_confirmed_absent') is True:
        late=at>due
        result.update(notification_evidence='CONFIRMED_ABSENT',status='OVERDUE_NOT_NOTIFIED' if late else 'OPEN',is_breach=late)
    else:result['status']='NOTIFICATION_STATUS_UNKNOWN' if at>due else 'OPEN'
    return result
