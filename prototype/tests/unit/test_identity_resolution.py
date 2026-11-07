from adjudication.identity.resolver import IdentityResolver

def test_alias_resolution(data):
    resolver=IdentityResolver(data["aliases"])
    result=resolver.resolve("Product One Alias","product",{"PROD-1"})
    assert result["canonical"]=="PROD-1" and result["method"]=="confirmed_alias"
