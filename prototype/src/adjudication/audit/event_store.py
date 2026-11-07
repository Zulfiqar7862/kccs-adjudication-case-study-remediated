def audit_rows(cases):
    rows=[]
    for case in cases:
        for e in case.events:
            rows.append({"event_id":e.event_id,"case_id":e.case_id,"event_type":e.event_type,"occurred_at":e.occurred_at.isoformat(),"actor":e.actor,"previous_state":e.previous_state,"new_state":e.new_state,"payload":e.payload})
    return rows
