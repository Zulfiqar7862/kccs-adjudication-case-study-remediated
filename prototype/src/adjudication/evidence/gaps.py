def evidence_gaps(case_id,study,storage_spec):
    gaps=[]
    if study is None: gaps.append({"case_id":case_id,"gap_type":"STABILITY_EVIDENCE_MISSING","severity":"high","detail":"No stability study could be resolved."})
    elif not study.readable: gaps.append({"case_id":case_id,"gap_type":"STABILITY_EVIDENCE_UNREADABLE","severity":"high","detail":"Stability study exists but has no readable outcome."})
    if not storage_spec: gaps.append({"case_id":case_id,"gap_type":"STORAGE_SPECIFICATION_MISSING","severity":"medium","detail":"No storage specification could be resolved."})
    return gaps
