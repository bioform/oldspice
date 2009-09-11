import ldap
from symantec.ssim.utils import ldaphelper

class Location:
    def __init__(self, search_result):
        self.host = search_result.get_attr_values('host')[0]
        self.addresses = search_result.get_attr_values('symcIPAddresses')
        self.address = self.addresses[0]
        self.dn = search_result.get_dn()
        self.name = search_result.get_attr_values('dlmName')[0]
        #parse datetime
        self.install_date = search_result.get_attr_values('dlmInstallDate')[0]
        self.install_date = ldaphelper.parse_generalized_time(self.install_date)

    def __str__(self):
        return self.host

def all(l, base_dn):
    filter = '(objectclass=dlm1ComputerSystem)'
    attrs = ['host','dlmInstallDate','dlmName','symcIPAddresses']
    raw_res = l.search_s( "ou=Locations,"+base_dn, ldap.SCOPE_SUBTREE, filter, attrs)
    search_result = ldaphelper.get_search_results( raw_res )
    list = [Location(item) for item in search_result]
    return list


