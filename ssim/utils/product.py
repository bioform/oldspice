import ldap
from symantec.ssim.utils import ldaphelper

class Product:
    def __init__(self, search_result):
        self.prodictID = search_result.get_attr_values('dlmIdentifyingNumber')[0]
        self.name = search_result.get_attr_values('dlmName')[0]
        self.version = search_result.get_attr_values('dlmVersion')[0]

    def __str__(self):
        return self.name

def all(l, base_dn):
    filter = '(dlmSKUNumber=*)'
    attrs = ['dlmIdentifyingNumber','dlmName','dlmVersion', 'dlmSKUNumber']
    raw_res = l.search_s( "cn=Products,ou=Applications,"+base_dn, ldap.SCOPE_SUBTREE, filter, attrs)
    search_result = ldaphelper.get_search_results( raw_res )
    list = [Product(item) for item in search_result]
    return list

