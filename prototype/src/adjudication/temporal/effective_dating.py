"""Half-open effective dates; overlapping authority is a conflict, not latest-wins."""
from dataclasses import asdict

def select_effective(sops,as_at,doc_id=None):
    candidates=[s for s in sops if (doc_id is None or s.doc_id==doc_id) and s.effective_from and s.effective_from<=as_at and (s.effective_to is None or s.effective_to>as_at)]
    if len(candidates)>1:raise ValueError('SOP_REVISION_CONFLICT')
    return candidates[0] if candidates else None

def resolve_sops(sops,tenant,as_at,origin,destination):
    candidates=[s for s in sops if tenant and s.tenant_code==tenant and (s.title or '').casefold()=='temperature excursion management' and s.effective_from and s.effective_from<=as_at and (s.effective_to is None or s.effective_to>as_at)]
    result={'as_at':as_at.isoformat(),'date_basis':'excursion_start_or_explicit_alert_fallback','tenant_code':tenant,'candidates':[asdict(s) for s in candidates],'eligible':[],'issues':[]}
    if not candidates:result['issues'].append('SOP_MISSING');return result
    for doc in {s.doc_id for s in candidates}:
        revisions=[s for s in candidates if s.doc_id==doc]
        if len(revisions)!=1:result['issues'].append('SOP_REVISION_CONFLICT');continue
        s=revisions[0];scope=(s.facilities or '').strip().casefold()
        if scope!='all sites':
            # No interpretation of free-text site names/annexures as an authoritative mapping.
            allowed={v.strip().casefold() for v in scope.split(',')}
            if not origin or not destination or origin.casefold() not in allowed or destination.casefold() not in allowed:result['issues'].append('SOP_FACILITY_UNVERIFIED');continue
        if 'annexure' in (s.acceptance_location or '').casefold():result['issues'].append('SOP_ANNEXURE_UNAVAILABLE');continue
        result['eligible'].append({'doc_id':s.doc_id,'revision':s.revision,'tenant_code':s.tenant_code})
        result['issues'].append('SOP_LIMITS_NOT_EXTRACTED')
    result['issues']=sorted(set(result['issues']))
    return result
