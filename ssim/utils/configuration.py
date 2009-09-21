import ldap
from symantec.ssim.utils import ldaphelper
from symantec.ssim.utils.ldaphelper import LDAPSearchResult
from symantec.ssim.utils import product

CONFIGURATION_ATTRS = ['dlmName','symcValid','dlmDescription','dlmSettingContextSettingRef','symcElementConfigurationElementRef', 'symcSequenceRevision']
SETTINGS_ATTRS = ['dlmCaption','binProperty','binPropertyType','dlmDescription','dlmSettingID','symcMetaData', 'symcSequenceRevision', 'symcValid']

class Configuration:
    def __init__(self, search_result):
        self.dn = search_result.get_dn()
        self.name = search_result.get_attr_values('dlmName')[0]

        if search_result.has_attribute('dlmDescription'):
            self.desc = search_result.get_attr_values('dlmDescription')
        else:
            self.desc = ''

        self.settings = search_result.get_attr_values('dlmSettingContextSettingRef')
        self.elements = search_result.get_attr_values('symcElementConfigurationElementRef')
        self.updated_at = search_result.get_attr_values('symcSequenceRevision')[0]
        self.updated_at = ldaphelper.parse_generalized_time(self.updated_at)

    def __str__(self):
        return self.name

class Settings:
    def __init__(self, search_result):
        self.dn = search_result.get_dn()
        self.name = search_result.get_attr_values('dlmCaption')[0]
        if search_result.has_attribute('binProperty'):
            self.data = search_result.get_attr_values('binProperty')[0]
        else:
            self.data = ''

        if search_result.has_attribute('binPropertyType'):
            self.data_type = search_result.get_attr_values('binPropertyType')[0]
        else:
            self.data_type = None

        if search_result.has_attribute('dlmDescription'):
            self.desc = search_result.get_attr_values('dlmDescription')[0]
        else:
            self.desc = ''
        self.settingID = search_result.get_attr_values('dlmSettingID')[0]
        self.metadata = search_result.get_attr_values('symcMetaData')[0]

        self.updated_at = search_result.get_attr_values('symcSequenceRevision')[0]
        self.updated_at = ldaphelper.parse_generalized_time(self.updated_at)

        self.is_valid = search_result.get_attr_values('symcValid')[0]
        if 'TRUE' == self.is_valid:
            self.is_valid = True
        else:
            self.is_valid = False


    def __str__(self):
        return self.name

def get_config_root(l, base_dn, productID):
    # get product
    product_instance = product.pruduct_by_id(l, base_dn, productID)

    if not product_instance:
        return None, None
    # get config link
    filter = '(symcFeatureUses=SESA_CONFIGURING)'
    attrs = ['dlmName','symcAppSysSWFGroupComponentRef']
    raw_res = l.search_s( product_instance.dn, ldap.SCOPE_SUBTREE, filter, attrs)
    config_root = ldaphelper.get_search_results( raw_res )[0]
    config_root = config_root.get_attr_values('symcAppSysSWFGroupComponentRef')[0]
    return product_instance, config_root

def configurations(l, base_dn, productID):
    # get root config
    product_instance, config_root = get_config_root(l, base_dn, productID)
    if not product_instance:
        return None, None, None
    # get config list
    filter = '(objectclass=symc1ElementConfiguration)'
    attrs = CONFIGURATION_ATTRS
    raw_res = l.search_s( "cn=Configs,%s" % config_root, ldap.SCOPE_SUBTREE, filter, attrs)
    list = [Configuration(item) for item in ldaphelper.get_search_results( raw_res )]
    return product_instance, config_root, list

def get_config_by_name(l, base_dn, productID, config_name):
    # get root config
    product_instance, config_dn = get_config_root(l, base_dn, productID)
    filter = '(&(objectclass=symc1ElementConfiguration)(dlmName=%s))' % config_name
    attrs = CONFIGURATION_ATTRS
    raw_res = l.search_s( "cn=Configs,%s" % config_dn, ldap.SCOPE_SUBTREE, filter, attrs)
    return product_instance, config_dn, Configuration(LDAPSearchResult(raw_res[0]))

def get_config_by_dn(l, configDN):
    # get root config
    filter = '(objectclass=symc1ElementConfiguration)'
    attrs = CONFIGURATION_ATTRS
    raw_res = l.search_s( configDN, ldap.SCOPE_BASE, filter, attrs)
    return Configuration(LDAPSearchResult(raw_res[0]))

def get_all_settings(l, config):
    all_settings = []
    filter = '(objectclass=*)'
    attrs = SETTINGS_ATTRS

    for item in config.settings:
        raw_res = l.search_s( item, ldap.SCOPE_BASE, filter, attrs)
        all_settings += [Settings(item) for item in ldaphelper.get_search_results( raw_res )]
    return all_settings

def get_sensor_config(l, config):
    all_settings = get_all_settings(l, config)
    for item in all_settings:
        if item.name == 'WorkingGroup Settings':
            return item
    return None
