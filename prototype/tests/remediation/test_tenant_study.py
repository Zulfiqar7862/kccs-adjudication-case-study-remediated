from dataclasses import replace
from adjudication.workflow.case_service import CaseService
from adjudication.domain.models import Product,Study

def test_tenant_specific_shared_sku(event,data):
    a=Product('SHARED','A pen','2-8','SA','A');b=Product('SHARED','B pen','2-8','SB','B')
    s=CaseService({**data,'products':[a,b],'studies':[Study('SA','SHARED',True,'ok','limit','A'),Study('SB','SHARED',True,'ok','limit','B')]})
    e=replace(event,product_ref='shared',raw={'tenant_code':'B'})
    c=s.create_case(e,e.alert_ts_utc)
    p=next(x.payload for x in c.events if x.event_type=='RECOMMENDATION_GENERATED')
    assert p['product_resolution']['tenant_code']=='B'
    assert p['study_eligibility']['study_ref']=='SB'

def test_real_products_and_named_tenant(workbook_data):
    assert len(workbook_data['products'])==59
    e=next(e for e in workbook_data['events'] if e.event_id=='EXC-112352')
    c=CaseService(workbook_data).create_case(e,e.alert_ts_utc)
    p=next(x.payload for x in c.events if x.event_type=='RECOMMENDATION_GENERATED')
    assert p['product_resolution']['tenant_code']=='T-PINNACLE'
    assert p['study_eligibility']['source_study_ref']=='STB-9543'

def test_wrong_presentation_blocks(event,data):
    a=Product('SKU','Glucodyne SoloJet 100U','2-8','VIAL','A')
    c=CaseService({**data,'products':[a],'studies':[Study('VIAL','Glucodyne 100U — vial',True,'ok','limit','A')]}).create_case(replace(event,product_ref='SKU',raw={'tenant_code':'A'}),event.alert_ts_utc)
    assert any(g['gap_type']=='STUDY_PRESENTATION_CONFLICT' for g in c.gaps)

def test_facility_resolution_cannot_cross_tenant(event,data):
    from adjudication.domain.models import Facility
    a=Facility('SHARED','Tenant A site','UTC','A')
    b=Facility('SHARED','Tenant B site','UTC','B')
    s=CaseService({**data,'facilities':[a,b]})
    e=replace(event,facility_ref='SHARED',raw={'tenant_code':'B'})
    r=s.resolve_facility(e)
    assert r['tenant_code']=='B' and r['canonical']=='SHARED'
    e.raw={}
    assert s.resolve_facility(e)['canonical'] is None

def test_matching_brand_and_presentation_does_not_attest_strength(event,data):
    from adjudication.domain.models import Product,Study
    p=Product('SKU','Glucodyne SoloJet 100U','2-8','S','A',source_row=2)
    s=Study('S','Glucodyne SoloJet 200U pen stability report',True,'ok','6 hours','A',source_row=3)
    c=CaseService({**data,'products':[p],'studies':[s]}).create_case(replace(event,product_ref='SKU',raw={'tenant_code':'A'}),event.alert_ts_utc)
    payload=next(x.payload for x in c.events if x.event_type=='RECOMMENDATION_GENERATED')
    assert payload['study_eligibility']['study_ref'] is None
    assert any(g['gap_type']=='STUDY_RELATIONSHIP_UNVERIFIED' for g in c.gaps)
