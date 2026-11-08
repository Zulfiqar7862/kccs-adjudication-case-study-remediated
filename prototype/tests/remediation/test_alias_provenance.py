from adjudication.domain.models import Alias
from adjudication.identity.resolver import IdentityResolver

def test_conflicting_aliases_abstain():
    r=IdentityResolver([Alias('x','a','product'),Alias('x','b','product')]).resolve('x','product',{'a','b'})
    assert r['canonical'] is None and r['method']=='conflict'

def test_target_existence_and_negative_evidence():
    assert IdentityResolver([Alias('x','absent','product')]).resolve('x','product',{'a'})['canonical'] is None
    rs=[Alias('x','a','product'),Alias('x','a','product',same=False)]
    assert IdentityResolver(rs).resolve('x','product',{'a'})['method']=='conflict'

def test_real_negative_provenance_preserved(workbook_data):
    negative=[a for a in workbook_data['aliases'] if a.same is False]
    assert len(negative)==4 and all(a.source_row and a.confirmed_by and a.comment for a in negative)
    r=IdentityResolver(workbook_data['aliases']).resolve('Schiphol Hub','facility',{'AMS-CS-01'})
    assert r['canonical'] is None and r['provenance']
