import ldap
from symantec.ssim.utils import ldaphelper
from xml.dom.minidom import parse, parseString


class Value:
    def __init__(self, node):
        self.type = node.getElementsByTagName("type")[0]
        self.text = getText(node.childNodes)

class Field:
    def __init__(self, node):
        self.byname = node.getElementsByTagName("byname")[0]
        self.byuser = node.getElementsByTagName("byuser")[0]
        self.id = node.getElementsByTagName("id")[0]
        self.name = node.getElementsByTagName("name")[0]
        self.type = node.getElementsByTagName("type")[0]

class Argument:
    def __init__(self, node):
        fieldNodes = node.getElementsByTagName("Field")
        if len(fieldNodes) > 0
            self.field = Field(fieldNodes[0])
        else
            self.field = None

        valueNodes = node.getElementsByTagName("Value")
        if len(fieldNodes) > 0
            self.value = Value(valueNodes[0])
        else
            self.value = None

class Condition:
    def __init__(self, node):
        self.operator = node.getElementsByTagName("operator")[0]
        self.arguments = []
        for c in node.getElementsByTagName("Argument")
            self.arguments += [Argument(c)]

class Criteria:
    def __init__(self, node):
        self.name = node.getElementsByTagName("name")[0]
        self.conditions = []
        for c in node.getElementsByTagName("Condition")
            self.conditions += [Condition(c)]

class Query:
    def __init__(self, xml):
            #parse XML
        dom = parseString(sensor_xml)
        #get all sensors
        query = dom.getElementsByTagName("query")[0]
        self.uid = query.getElementsByTagName("uid")[0]
        self.treetype = query.getElementsByTagName("treetype")[0]
        self.type = query.getElementsByTagName("querytype")[0]
        self.name = query.getElementsByTagName("query_name")[0]

        timerange = query.getElementsByTagName("timerange")[0]
        self.timerangetype = timerange.getElementsByTagName("timerangetype")[0]
        self.timerangevalue = timerange.getElementsByTagName("value")[0]

        self.criterias = []
        for c in query.getElementsByTagName("criteria")
            self.criterias += [Criteria(c)]

class QueryDef:
    def __init__(self, search_result):
        self.dn = search_result.get_dn()
        self.id = search_result.get_attr_values('dlmSettingID')[0]
        self.name = search_result.get_attr_values('dlmCaption')[0]

        self.query = Query(search_result.get_attr_values('binProperty')[0])

        if  search_result.has_attribute('symcSequenceRevision'):
            self.updated_at = search_result.get_attr_values('symcSequenceRevision')[0]
            self.updated_at = ldaphelper.parse_generalized_time(self.updated_at)
        else:
            self.updated_at = datetime.now()


    def __str__(self):
        return self.name

    def __eq__(self, y):
        return self.productID == y.productID

    def __hash__(self):
        return self.productID.__hash__()

def get_custom_queries(l, base_dn):
    filter = '(objectclass=symc1SettingInstance)'
    attrs = ['dlmSettingID','dlmCaption','binProperty', 'symcProductVersion']
    raw_res = l.search_s( "cn=Custom Queries,cn=Queries,ou=Administration,"+base_dn, ldap.SCOPE_SUBTREE, filter, attrs)
    search_result = ldaphelper.get_search_results( raw_res )
    list = [QueryDef(item) for item in search_result]
    return list

def get_system_queries(l, base_dn):
    filter = '(objectclass=symc1SettingInstance)'
    attrs = ['dlmSettingID','dlmCaption','binProperty', 'symcProductVersion']
    raw_res = l.search_s( "cn=cn=System Queries,cn=Queries,ou=Administration,dc=Symantec,dc=SES,O=SYMC_SES Queries,cn=Queries,ou=Administration,"+base_dn, ldap.SCOPE_SUBTREE, filter, attrs)
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