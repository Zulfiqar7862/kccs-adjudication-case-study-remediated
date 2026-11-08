from datetime import timedelta
from adjudication.temporal.clock import calculate_clock as assess, NotificationPolicy

def calculate_clock(event,**kwargs):
    return assess(event,policy=NotificationPolicy("SYNTHETIC-48H","hours",48),**kwargs)

def test_clock_uses_alert_time(event):
    status=calculate_clock(event,evaluated_at=event.alert_ts_utc+timedelta(hours=10))
    assert status["notification_due_at"]==(event.alert_ts_utc+timedelta(hours=48)).isoformat()
    assert status["hours_remaining"]==38 and status["status"]=="OPEN"

def test_known_late_notification(event):
    event.hours_to_notification=50.0
    status=calculate_clock(event,evaluated_at=event.alert_ts_utc+timedelta(hours=73))
    assert status["status"]=="NOTIFIED_LATE" and status["is_breach"]

def test_unknown_notification_is_not_breach(event):
    event.hours_to_notification=None
    status=calculate_clock(event,evaluated_at=event.alert_ts_utc+timedelta(hours=73))
    assert status["status"]=="NOTIFICATION_STATUS_UNKNOWN"
    assert status["notified"] is None and not status["is_breach"]
