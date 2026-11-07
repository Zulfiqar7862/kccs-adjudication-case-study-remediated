from datetime import datetime, timezone
from adjudication.temporal.effective_dating import select_effective
from adjudication.domain.models import SOP

def test_selects_effective_sop():
    sops=[SOP("SOP-1","v1",datetime(2025,1,1,tzinfo=timezone.utc),datetime(2026,1,1,tzinfo=timezone.utc),None),SOP("SOP-1","v2",datetime(2026,1,1,tzinfo=timezone.utc),None,None)]
    assert select_effective(sops,datetime(2026,6,1,tzinfo=timezone.utc),"SOP-1").revision=="v2"
