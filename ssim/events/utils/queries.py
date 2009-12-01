import ldap
from symantec.ssim.utils import ldaphelper
from xml.dom.minidom import parse, parseString
from datetime import datetime


class Value:
    def __init__(self, node):
        typeNodes = node.getElementsByTagName("type")
        if len(typeNodes) > 0:
            self.type = typeNodes[0]

        self.text = getText(node.childNodes)

class Field:
    def __init__(self, node):

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

class Argument:
    def __init__(self, node):
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

class Condition:
    def __init__(self, node):
        operatorNodes = node.getElementsByTagName("operator")
        if len(operatorNodes) > 0:
            self.operator = operatorNodes[0]
        else:
            self.operator = None
            
        self.arguments = []
        for c in node.getElementsByTagName("Argument"):
            self.arguments += [Argument(c)]

class Criteria:
    def __init__(self, node):
        nameNodes = node.getElementsByTagName("name")
        if len(nameNodes) > 0:
            self.name = nameNodes[0]
        else:
            self.name = None
            
        self.conditions = []
        for c in node.getElementsByTagName("Condition"):
            self.conditions += [Condition(c)]

class Query:
    def __init__(self, xml):
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

class QueryDef:
    def __init__(self, search_result):
        self.dn = search_result.get_dn()
        self.id = search_result.get_attr_values('dlmSettingID')[0]
        self.name = search_result.get_attr_values('dlmCaption')[0]

        self.bin_property = search_result.get_attr_values('binProperty')[0]

        if  search_result.has_attribute('symcSequenceRevision'):
            self.updated_at = search_result.get_attr_values('symcSequenceRevision')[0]
            self.updated_at = ldaphelper.parse_generalized_time(self.updated_at)
        else:
            self.updated_at = datetime.now()

    def extract_query(self):
        self.query = Query(self.bin_property)
        return self.query

    def __str__(self):
        return self.name

    def __eq__(self, y):
        return self.productID == y.productID

    def __hash__(self):
        return self.productID.__hash__()

def get_query(l, query_dn):
    filter = '(objectclass=symc1SettingInstance)'
    attrs = ['dlmSettingID','dlmCaption','binProperty', 'symcProductVersion']
    raw_res = l.search_s( query_dn, ldap.SCOPE_BASE, filter, attrs)
    search_result = ldaphelper.get_search_results( raw_res )
    query_def = QueryDef(search_result[0])
    return query_def.extract_query()

def get_custom_queries(l, base_dn):
    filter = '(objectclass=symc1SettingInstance)'
    attrs = ['dlmSettingID','dlmCaption', 'symcProductVersion']
    raw_res = l.search_s( "cn=Custom Queries,cn=Queries,ou=Administration,"+base_dn, ldap.SCOPE_SUBTREE, filter, attrs)
    search_result = ldaphelper.get_search_results( raw_res )
    list = [QueryDef(item) for item in search_result]
    return list

def get_system_queries(l, base_dn):
    filter = '(objectclass=symc1SettingInstance)'
    attrs = ['dlmSettingID','dlmCaption','binProperty', 'symcProductVersion']
    raw_res = l.search_s( "cn=System Queries,cn=Queries,ou=Administration,"+base_dn, ldap.SCOPE_SUBTREE, filter, attrs)
    search_result = ldaphelper.get_search_results( raw_res )
    list = [QueryDef(item) for item in search_result]
    return list

#######################################################################################
def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc