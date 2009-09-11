import ldap
from symantec.ssim.utils import ldaphelper

class Product:
    def __init__(self, search_result):
        # get product ID
        attr = 'dlmIdentifyingNumber'
        if search_result.has_attribute('symcProductIdentifyingNumber'):
            attr = 'symcProductIdentifyingNumber'
        self.productID = search_result.get_attr_values(attr)[0]
        # get product name
        attr = 'dlmName'
        if search_result.has_attribute('symcProductName'):
            attr = 'symcProductName'
        self.name = search_result.get_attr_values(attr)[0]
        # get product version
        attr = 'dlmVersion'
        if search_result.has_attribute('symcProductVersion'):
            attr = 'symcProductVersion'
        self.version = search_result.get_attr_values(attr)[0]

    def __str__(self):
        return self.name
    
    def __eq__(self, y):
        return self.productID == y.productID

    def __hash__(self):
        return self.productID.__hash__()

def all(l, base_dn):
    filter = '(dlmSKUNumber=*)'
    attrs = ['dlmIdentifyingNumber','dlmName','dlmVersion', 'dlmSKUNumber']
    raw_res = l.search_s( "cn=Products,ou=Applications,"+base_dn, ldap.SCOPE_SUBTREE, filter, attrs)
    search_result = ldaphelper.get_search_results( raw_res )
    list = filter_pruducts([Product(item) for item in search_result])
    return list

def client_products(l, base_dn):
    filter = '(objectclass=symc1SoftwareInstance)'
    attrs = ['symcProductIdentifyingNumber','dlmName','symcProductName', 'symcProductVersion']
    raw_res = l.search_s( base_dn, ldap.SCOPE_SUBTREE, filter, attrs)
    search_result = ldaphelper.get_search_results( raw_res )
    list = filter_pruducts([Product(item) for item in search_result])
    return list

def configurations(l, base_dn, productID):
    filter = '(dlmSKUNumber=*)'
    attrs = ['dlmIdentifyingNumber','dlmName','dlmVersion', 'dlmSKUNumber']
    raw_res = l.search_s( "cn=Products,ou=Applications,"+base_dn, ldap.SCOPE_SUBTREE, filter, attrs)
    search_result = ldaphelper.get_search_results( raw_res )
    list = [Product(item) for item in search_result]
    return list

def filter_pruducts(pruduct_list):
    return set([p for p in pruduct_list if p.productID not in ['3000','3014'] ])
