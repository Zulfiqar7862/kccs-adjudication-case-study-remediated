from datetime import timedelta
from adjudication.temporal.clock import calculate_clock

def test_clock_uses_alert_time(event):
    status=calculate_clock(event,evaluated_at=event.alert_ts_utc+timedelta(hours=10))
    assert status["notification_due_at"]==(event.alert_ts_utc+timedelta(hours=48)).isoformat()
    assert status["hours_remaining"]==38 and status["status"]=="OPEN"

def test_clock_overdue(event):
    status=calculate_clock(event,evaluated_at=event.alert_ts_utc+timedelta(hours=73))
    assert status["status"]=="OVERDUE_NOT_NOTIFIED" and status["is_breach"]
