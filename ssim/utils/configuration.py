import ldap
import uuid
import re
from symantec.ssim.utils import ldaphelper
from symantec.ssim.utils.ldaphelper import LDAPSearchResult
from symantec.ssim.utils import product
from datetime import datetime

CONFIGURATION_ATTRS = ['dlmName','symcValid','dlmDescription','dlmSettingContextSettingRef','symcElementConfigurationElementRef', 'symcSequenceRevision']
SETTINGS_ATTRS = ['dlmCaption','binProperty','binPropertyType','dlmDescription','dlmSettingID','symcMetaData', 'symcSequenceRevision', 'symcValid']
CONFIG_SPECIFIED_ATTRS = ['dlmSettingContextSettingRef', 'orderedCimKeys', 'dlmCaption', 'dlmDescription', 'symcSequenceName', 'dlmName', 'symcElementConfigurationElementRef']
SETTINGS_SPECIFIED_ATTRS = ['dlmSettingID', 'symcSequenceName', 'orderedCimKeys']

class Configuration:
    def __init__(self, search_result):
        self.search_result = search_result;
        self.dn = search_result.get_dn()
        self.name = search_result.get_attr_values('dlmName')[0]

        if search_result.has_attribute('dlmDescription'):
            self.desc = search_result.get_attr_values('dlmDescription')[0]
        else:
            self.desc = ''

        self.settings = search_result.get_attr_values('dlmSettingContextSettingRef')
        
        if search_result.has_attribute('symcElementConfigurationElementRef'):
            self.elements = search_result.get_attr_values('symcElementConfigurationElementRef')
        else:
            self.elements = None;

        if  search_result.has_attribute('symcSequenceRevision'):
            self.updated_at = search_result.get_attr_values('symcSequenceRevision')[0]
            self.updated_at = ldaphelper.parse_generalized_time(self.updated_at)
        else:
            self.updated_at = datetime.now()

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

def get_default_config(l, base_dn, productID):
    # get root config
    product_instance, config_dn = get_config_root(l, base_dn, productID)
    filter = '(&(!(objectclass=symc1ElementConfiguration))(dlmName=Default))'
    raw_res = l.search_s( "cn=Configs,%s" % config_dn, ldap.SCOPE_SUBTREE, filter)
    return product_instance, config_dn, Configuration(LDAPSearchResult(raw_res[0]))

def copy_dafault_config(l, base_dn, productID, new_config_name):
    product_instance, config_dn, config = get_default_config(l, base_dn, productID)
    new_config_dn = config.dn.replace(config.name, new_config_name, 1)
    #create config for all tabs
    all_settings_dn = []
    for setting_dn in config.settings:
        all_settings_dn += [duplicate_settings(l, setting_dn)]
    #create config
    add_record = [
                    ('objectclass', 'symc1ElementConfiguration'),
                    ('objectclass', 'symc1ElementConfigurationAuxClass'),
                    ('dlmCaption', new_config_name),
                    ('dlmName', new_config_name),
                    ('orderedCimKeys', "CIM_Configuration.Name=%s" % new_config_name),
                 ]
    # add settings references
    for setting_dn in all_settings_dn:
        add_record += [('dlmSettingContextSettingRef', setting_dn)]
    # copy all attributes
    search_result = config.search_result
    for attr in search_result.get_attr_names():
        if attr not in CONFIG_SPECIFIED_ATTRS:
            for value in search_result.get_attr_values(attr):
                add_record += [(attr, value)]

    print "===>", add_record
    l.add_s(new_config_dn, add_record)
    return new_config_dn

def duplicate_settings(l, setting_dn):
    new_uid = str(uuid.uuid1())
    new_orderedCimKeys = 'Symc_Setting.SettingID=%s' % new_uid
    # create new settings DN
    dn_suffix = re.match('.+?(,.+)', setting_dn)
    new_setting_dn = 'orderedCimKeys=' + new_orderedCimKeys.replace('=','\=') + dn_suffix.group(1)
    #new_setting_dn = new_setting_dn.replace('-','')
    # prepare new settings attributes
    add_record = [
                    ('dlmSettingID', new_uid),
                    ('symcSequenceName', new_uid),
                    ('orderedCimKeys', new_orderedCimKeys),
                 ]
    #get all attributes
    filter = '(objectclass=*)'
    raw_res = l.search_s( setting_dn, ldap.SCOPE_BASE, filter)
    search_result = ldaphelper.get_search_results( raw_res )[0]
    # add all attributes to new record
    for attr in search_result.get_attr_names():
        if attr not in SETTINGS_SPECIFIED_ATTRS:
            for value in search_result.get_attr_values(attr):
                add_record += [(attr, value)]
                
    l.add_s(new_setting_dn, add_record)
    
    return new_setting_dn

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

def update_settings(l, dn, xml):
    mod_attrs = [( ldap.MOD_REPLACE, 'binProperty', xml.encode("utf-8") )]
    l.modify_s(dn, mod_attrs)
