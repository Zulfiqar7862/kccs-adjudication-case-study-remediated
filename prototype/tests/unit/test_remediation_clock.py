from dataclasses import replace
from datetime import timedelta, datetime, timezone
from adjudication.temporal.clock import calculate_clock, NotificationPolicy

def test_nonreportable_has_no_obligation(event):
    r=calculate_clock(replace(event,regulator_reportable=False,reg_window_hours=None),event.alert_ts_utc+timedelta(days=10))
    assert r['status']=='NOT_APPLICABLE' and r['notification_due_at'] is None

def test_absent_policy_never_defaults(event):
    r=calculate_clock(replace(event,regulator_reportable=True,reg_window_hours=None),event.alert_ts_utc+timedelta(days=10))
    assert r['status']=='POLICY_UNKNOWN' and not r['is_breach']

def test_unknown_applicability_is_not_false(event):
    r=calculate_clock(replace(event,regulator_reportable=None),event.alert_ts_utc)
    assert r['applicability']=='UNKNOWN' and r['status']=='APPLICABILITY_UNKNOWN'

def test_unknown_receipt_vs_proved_absence(event):
    e=replace(event,regulator_reportable=True)
    assert calculate_clock(e,e.alert_ts_utc+timedelta(days=3),policy=NotificationPolicy('SYNTHETIC','hours',48))['status']=='NOTIFICATION_STATUS_UNKNOWN'
    e.raw={'notification_confirmed_absent':True}
    assert calculate_clock(e,e.alert_ts_utc+timedelta(days=3),policy=NotificationPolicy('SYNTHETIC','hours',48))['status']=='OVERDUE_NOT_NOTIFIED'

def test_receipt_exact_boundary_and_future_receipt(event):
    e=replace(event,regulator_reportable=True,hours_to_notification=48)
    assert calculate_clock(e,e.alert_ts_utc+timedelta(hours=49),policy=NotificationPolicy('SYNTHETIC','hours',48))['status']=='NOTIFIED_WITHIN_WINDOW'
    assert calculate_clock(e,e.alert_ts_utc+timedelta(hours=2),policy=NotificationPolicy('SYNTHETIC','hours',48))['notification_evidence']=='NOT_YET_OBSERVED'

def test_explicit_business_calendar_requires_context(event):
    from adjudication.temporal.clock import NotificationPolicy
    e=replace(event,regulator_reportable=True,reg_window_hours=None,alert_ts_utc=datetime(2026,1,2,12,tzinfo=timezone.utc))
    p=NotificationPolicy('US_TEST','next_business_day',timezone='America/New_York',calendar_id='TEST-weekends-holidays-v1',holidays=('2026-01-05',),cutoff='17:00')
    r=calculate_clock(e,e.alert_ts_utc,policy=p)
    assert r['notification_due_at']=='2026-01-06T22:00:00+00:00'
    assert calculate_clock(e,e.alert_ts_utc,policy=NotificationPolicy('US_UNSPECIFIED','next_business_day'))['status']=='POLICY_UNKNOWN'

def test_unknown_jurisdiction_is_not_legal_breach_even_with_extracted_window(event):
    e=replace(event,regulator_reportable=True,hours_to_notification=100,raw={})
    r=calculate_clock(e,e.alert_ts_utc+timedelta(days=10))
    assert r['status']=='POLICY_UNKNOWN' and not r['is_breach']
    assert r['source_window_assessment']=='EXTRACTED_RECEIPT_AFTER_WINDOW'

def test_receipt_evidence_is_independent_of_unknown_policy(event):
    e=replace(event,regulator_reportable=True,hours_to_notification=100,raw={})
    r=calculate_clock(e,e.alert_ts_utc+timedelta(days=10))
    assert r['status']=='POLICY_UNKNOWN' and r['notification_evidence']=='EXTRACTED_RECEIPT'
    assert r['notified'] is True and not r['is_breach']

def test_brazil_requires_explicit_local_timezone(event):
    e=replace(event,regulator_reportable=True,raw={'jurisdiction':'BR'})
    assert calculate_clock(e,e.alert_ts_utc)['status']=='POLICY_UNKNOWN'
    e.raw['notification_timezone']='America/Sao_Paulo'
    assert calculate_clock(e,e.alert_ts_utc)['notification_due_at']==(e.alert_ts_utc+timedelta(days=5)).isoformat()

def test_calendar_days_follow_local_wall_time_across_dst():
    from adjudication.temporal.clock import policy_due
    from datetime import datetime
    p=NotificationPolicy('SYNTHETIC-CALENDAR','calendar_days',timezone='America/New_York',days=5)
    a=datetime.fromisoformat('2026-03-06T12:00:00+00:00')
    assert (policy_due(a,p)-a).total_seconds()==119*3600

def test_settings_do_not_suggest_a_default_legal_window():
    from adjudication.config import load_settings
    assert load_settings().default_reg_window_hours is None
