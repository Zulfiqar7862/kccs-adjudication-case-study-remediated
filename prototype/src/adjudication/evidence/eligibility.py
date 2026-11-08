"""Conservative metadata eligibility; not document extraction or stability arithmetic."""
import re

def presentation(text):
    t=(text or '').casefold()
    if 'vial' in t:return 'vial'
    if any(v in t for v in ('pfs','pre-filled syringe','prefilled syringe')):return 'syringe'
    if 'solojet' in t or re.search(r'\bpen\b',t):return 'pen'
    return None

def study_eligibility(product,studies,tenant):
    result={'source_study_ref':product.stability_study_ref if product else None,'study_ref':None,'tenant_code':tenant,'issues':[]}
    if not product or not tenant:return None,result
    matches=[s for s in studies if s.study_ref==product.stability_study_ref]
    if not matches:return None,result
    owned=[s for s in matches if s.tenant_code==tenant]
    if len(owned)!=1:result['issues'].append('STUDY_TENANT_OR_REFERENCE_CONFLICT');return None,result
    s=owned[0];pp=presentation(product.product_name);sp=presentation(s.product_ref)
    # Exact canonical identifier is an explicit synthetic/source relationship;
    # human-written study descriptions require presentation and molecule checks.
    if not (product.source_row is None and s.product_ref==product.product_ref):
        if s.product_ref==product.product_name:result['issues'].append('STUDY_RELATIONSHIP_UNVERIFIED')
        if pp and sp and pp!=sp:result['issues'].append('STUDY_PRESENTATION_CONFLICT')
        elif pp is None or sp is None:result['issues'].append('STUDY_PRESENTATION_UNVERIFIED')
        if (product.product_name or '').split() and (product.product_name or '').split()[0].casefold() not in (s.product_ref or '').casefold():result['issues'].append('STUDY_PRODUCT_UNVERIFIED')
    if not s.readable:result['issues'].append('STUDY_READABILITY_UNVERIFIED')
    if not s.permitted_excursion_text:result['issues'].append('STUDY_PURPOSE_NOT_EXCURSION')
    if result['issues']:return None,result
    result['study_ref']=s.study_ref
    return s,result
