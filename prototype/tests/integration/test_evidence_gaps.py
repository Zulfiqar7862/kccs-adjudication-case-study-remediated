from adjudication.evidence.gaps import evidence_gaps

def test_missing_study():
    gaps=evidence_gaps("C1",None,None)
    assert any(g["gap_type"]=="STABILITY_EVIDENCE_MISSING" for g in gaps)
