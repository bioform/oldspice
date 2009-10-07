import ldap
from symantec.ssim.utils import ldaphelper

class Location:
    def __init__(self, search_result):
        self.dn = search_result.dn
        self.host = search_result.get_attr_values('host')[0]
        self.addresses = search_result.get_attr_values('symcIPAddresses')
        self.address = self.addresses[0]
        self.dn = search_result.get_dn()
        self.name = search_result.get_attr_values('dlmCaption')[0]
        #parse datetime
        self.install_date = search_result.get_attr_values('dlmInstallDate')[0]
        self.install_date = ldaphelper.parse_generalized_time(self.install_date)

    def __eq__(self,other):
        if other != None and self.dn == other.dn:
            return True
        else:
            return False
    
    def __hash__(self):
        return hash(self.dn)

    def __str__(self):
        return self.host

def all(l, base_dn, name_list = None):
    filter = '(objectclass=dlm1ComputerSystem)'
    if name_list and len(name_list) > 0:
        filter = '(&' + filter + '(|'
        for name in name_list:
            filter += '(dlmName=%s)' % name
        filter += '))'
    attrs = ['host','dlmInstallDate','dlmName', 'dlmCaption','symcIPAddresses']
    raw_res = l.search_s( "ou=Locations,"+base_dn, ldap.SCOPE_SUBTREE, filter, attrs)
    search_result = ldaphelper.get_search_results( raw_res )
    list = [Location(item) for item in search_result]
    return list

def client_dn(l, base_dn, clientAddress):
    filter = '(symcIPAddresses=%s)' % clientAddress
    attrs = ['host','dlmInstallDate','dlmName', 'dlmCaption', 'symcIPAddresses']
    raw_res = l.search_s( "ou=Locations,"+base_dn, ldap.SCOPE_SUBTREE, filter, attrs)
    search_result = ldaphelper.get_search_results( raw_res )
    return search_result[0].get_dn()


