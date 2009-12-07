import ldap
from symantec.ssim.utils import ldaphelper
from xml.dom.minidom import parse, parseString
from datetime import datetime

class Archive:
    def __init__(self, xml):
        document = parseString(xml)
        self.descr = getText( document.getElementsByTagName('Description')[0].childNodes )
        archiveNode = document.getElementsByTagName('Archive')[0]
        self.name = archiveNode.getAttribute('name')
        self.id = archiveNode.getAttribute('id')

    def __str__(self):
        return '[' + self.id + ':' + self.name + ']'

class ArchiveDef:
    def __init__(self, search_result):
        self.dn = search_result.get_dn()
        self.name = search_result.get_attr_values('dlmCaption')[0]
        self.descr = search_result.get_attr_values('dlmDescription')[0]
        self.archive = Archive( search_result.get_attr_values('symcMetaData')[0] )

    def __str__(self):
        return self.name

class ArchiveDefContainer:
    def __init__(self, search_result):
        self.dn = search_result.get_dn()
        self.name = search_result.get_attr_values('dlmCaption')[0]
        self.descr = search_result.get_attr_values('dlmDescription')[0]
        self.members = [member for member in search_result.get_attr_values('member') if member != 'cn=this']

    def __str__(self):
        return self.name

def get_archives(l, base_dn):
    filter = '(objectclass=*)'
    attrs = ['dlmCaption','dlmDescription','member']
    raw_res = l.search_s( "cn=Archiving,cn=Rule Groups,cn=Rule Engine,cn=SIM,ou=Administration,"+base_dn, ldap.SCOPE_ONELEVEL, filter, attrs)
    search_results = ldaphelper.get_search_results( raw_res )
    archive_def_containers = [ArchiveDefContainer(search_result) for search_result in search_results]
    #get ArchiveDefs by definition DN
    archives = []
    for archive_def_container in archive_def_containers:
        for archive_def_dn in archive_def_container.members:
            filter = '(objectclass=*)'
            attrs = ['dlmCaption','dlmDescription','symcMetaData']
            raw_res = l.search_s( archive_def_dn, ldap.SCOPE_BASE, filter, attrs)
            search_results = ldaphelper.get_search_results( raw_res )
            #should be only one search result
            archives += [ ArchiveDef(search_results[0]).archive ]

    return archives

    



#######################################################################################
def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc