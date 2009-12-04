import ldap
from symantec.ssim.utils import ldaphelper
from xml.dom.minidom import parse, parseString
from datetime import datetime


class Value:
    def __init__(self, node = None):
        if not node:
            self.text = None
            self.type = None
            return
        typeNodes = node.getElementsByTagName("type")
        if len(typeNodes) > 0:
            self.type = typeNodes[0]

        self.text = getText(node.childNodes)

    def __str__(self):
        return self.text

class Field:
    def __init__(self, node = None):
        if not node:
            self.name = None
            self.type = None
            return
        bynameNodes = node.getElementsByTagName("byname")
        if len(bynameNodes) > 0:
            self.byname = [0]

        byuserNodes = node.getElementsByTagName("byuser")
        if len(byuserNodes):
            self.byuser = byuserNodes[0]

        idNodes = node.getElementsByTagName("id")
        if len(idNodes) > 0:
            self.id = idNodes[0]

        nameNodes = node.getElementsByTagName("name")
        if len(nameNodes) > 0:
            self.name = nameNodes[0]

        typeNodes = node.getElementsByTagName("type")
        if len(typeNodes) > 0:
            self.type = typeNodes[0]

    def __str__(self):
        return self.name


class Argument:
    def __init__(self, node = None):
        if not node:
            self.field = None
            self.value = None
            return
        fieldNodes = node.getElementsByTagName("Field")
        if len(fieldNodes) > 0:
            self.field = Field(fieldNodes[0])
        else:
            self.field = None
        valueNodes = node.getElementsByTagName("Value")

        if len(valueNodes) > 0:
            self.value = Value(valueNodes[0])
        else:
            self.value = None

    def __str__(self):
        return "{field: %s, value: %s}" % (self.field, self.value)

class Condition:
    def __init__(self, node = None):
        if not node:
            self.operator = None
            self.arguments = []
            return
        self.operator = node.getAttribute("operator")
            
        self.arguments = []
        for c in node.getElementsByTagName("Argument"):
            self.arguments += [Argument(c)]

    def __str__(self):
        return "opreator: '%s', args: [%s]" % (self.operator, ", ".join(["%s" % el for el in self.arguments]))

class Criteria:
    def __init__(self, node = None):
        if not node:
            return
        nameNodes = node.getElementsByTagName("name")
        if len(nameNodes) > 0:
            self.name = nameNodes[0]
        else:
            self.name = None
            
        self.conditions = []
        for c in node.getElementsByTagName("Condition"):
            self.conditions += [Condition(c)]

class Query:

    def __init__(self, xml = None):
        if not xml:
            return
        #parse XML
        dom = parseString(xml)
        #get all sensors
        query = dom.getElementsByTagName("query")[0]
        self.uid = query.getElementsByTagName("uid")[0]
        self.treetype = query.getElementsByTagName("treetype")[0]
        self.type = query.getElementsByTagName("querytype")[0]
        self.name = query.getElementsByTagName("query_name")[0]

        if len(query.getElementsByTagName("timerange")) > 0:
            timerange = query.getElementsByTagName("timerange")[0]

            timerangetypeNodes = timerange.getElementsByTagName("timerangetype")
            if len(timerangetypeNodes) > 0:
                self.timerangetype = getText( timerangetypeNodes[0].childNodes)

            valueNodes = timerange.getElementsByTagName("value")
            if len(valueNodes) > 0:
                self.timerangevalue = getText( valueNodes[0].childNodes)
        else:
            timerange = None

        self.criterias = []
        for c in query.getElementsByTagName("criteria"):
            self.criterias += [Criteria(c)]

        #EventCriteria and SecondaryEventCriteria
        self.event_criterias = []
        for c in query.getElementsByTagName("EventCriteria"):
            self.event_criterias += [Criteria(c)]


class QueryDef:
    def __init__(self, search_result):
        self.dn = search_result.get_dn()
        self.id = search_result.get_attr_values('dlmSettingID')[0]
        self.name = search_result.get_attr_values('dlmCaption')[0]
        self.orderedCimKeys = search_result.get_attr_values('orderedCimKeys')[0]

        if  search_result.has_attribute('binProperty'):
            self.bin_property = search_result.get_attr_values('binProperty')[0]

        if  search_result.has_attribute('symcSequenceRevision'):
            self.updated_at = search_result.get_attr_values('symcSequenceRevision')[0]
            self.updated_at = ldaphelper.parse_generalized_time(self.updated_at)
        else:
            self.updated_at = datetime.now()

    def extract_query(self):
        if self.bin_property:
            self.query = Query(self.bin_property)
        return self.query

    def __str__(self):
        return self.name

class QueryGroupDef:
    def __init__(self, search_result):
        self.cn = search_result.get_attr_values('cn')[0]
        self.dn = search_result.get_dn()
        self.name = search_result.get_attr_values('dlmCaption')[0]
        self.members = search_result.get_attr_values('member')
        self.queries = []

    def add(self, query_def):
        self.queries += [query_def]

    def add_all(self, query_def_list):
        self.queries += query_def_list

    def __str__(self):
        return self.name

def get_query(l, query_dn):
    filter = '(objectclass=symc1SettingInstance)'
    attrs = ['dlmSettingID','dlmCaption','binProperty', 'symcProductVersion']
    raw_res = l.search_s( query_dn, ldap.SCOPE_BASE, filter, attrs)
    search_result = ldaphelper.get_search_results( raw_res )
    query_def = QueryDef(search_result[0])
    return query_def.extract_query()

def get_system_query_groups(l, base_dn):
    filter = '(objectclass=*)'
    attrs = ['cn', 'member','dlmCaption','orderedCimKeys', 'dlmCreationClassName']
    raw_res = l.search_s( "cn=/,cn=System Query Groups,cn=Queries,ou=Administration,"+base_dn, ldap.SCOPE_ONELEVEL, filter, attrs)
    search_result = ldaphelper.get_search_results( raw_res )
    list = [QueryGroupDef(item) for item in search_result]
    return list

def get_query_groups(l, base_dn):
    filter = '(objectclass=*)'
    attrs = ['cn', 'member','dlmCaption','orderedCimKeys', 'dlmCreationClassName']
    raw_res = l.search_s( "cn=/,cn=Query Groups,cn=Queries,ou=Administration,"+base_dn, ldap.SCOPE_ONELEVEL, filter, attrs)
    search_result = ldaphelper.get_search_results( raw_res )
    list = [QueryGroupDef(item) for item in search_result]
    return list

#######################################################################################
def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc