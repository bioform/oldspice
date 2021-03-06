import urllib, urllib2, httplib, openanything
import ldap
import sys
import ssl
import traceback
from django.conf import settings
from datetime import datetime
from symantec.ssim.exceptions import *
from symantec.ssim.utils import cookie_processor
from xml.dom.minidom import parse, parseString

def get_auth_xml(address, login, password):
    print "Try connect to SSIM", address
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <ssmcRequest requestID="1251719297259" sessionID="">
                    <login timeZoneID="GMT" domain="" clientip="" user="%s" password="%s">
                            <locale countryCode="RU" languageCode="ru" variant=""/>
                    </login>
    </ssmcRequest>
    """ % (login, password)

    #print "\n--------------------------\n",xml,"\n--------------------------\n"

    conn = httplib.HTTPSConnection(address, timeout=10)

    data1 = ""
    conn.putrequest("POST", "/sesa/servlet/Admin")
    conn.putheader("Content-type", "text/xml; charset=UTF-8")
    conn.putheader("Content-length", "%d" % len(xml))
    conn.endheaders()
    conn.send(xml)
    r1 = conn.getresponse()
    data1 = r1.read()
    conn.close()

    if len(data1) != 0:
        return data1
    return ""

def get_ldap_connection(session, address, force = False):
    #clear cache
    clear_ldap_cache()
    # Get session data

    ldap_connections_key = address+"__"+session.session_key
    #try to get LDAP connection from key
    l = settings.LDAP_CONNECTIONS.get(ldap_connections_key, None)

    if 'ldap' not in session.keys():
        return l
    elif address not in session['ldap'].keys():
        return l
    elif force or l == None:
        # get session info
        data = session['ldap'][address]
        userDN = data['userDN']
        password = data['password']

        print "Connecting to LDAP", address
        server = 'ldaps://%s' % (address)

        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        l = ldap.initialize(server)
        #l.start_tls_s()
        l.simple_bind_s(userDN, password)
        settings.LDAP_CONNECTIONS[ldap_connections_key] = {'connection':l,'updated_at':datetime.now()}
    else:
        print "Get LDAP connection (%s) from cache" % (address)
        l['updated_at'] = datetime.now();
        l = l['connection']
    return l

def clear_ldap_cache():
    for key in settings.LDAP_CONNECTIONS.keys():
        l = settings.LDAP_CONNECTIONS[key]
        updated_at = l['updated_at']
        if (datetime.now() - updated_at).seconds > 1800:
            del settings.LDAP_CONNECTIONS[key]
            print "Removing \"%s\" LDAP connection" % key

def ldap_authenticate(session, address, login, password):
    # Serialize the result of the database retrieval to JSON and send an application/json response
    try:
        xml = get_auth_xml(address,login,password);
    except Exception, err:
        raise DefaultDomainException, "ERROR: %s" % err

    if len(xml) == 0:
        raise DefaultDomainException, "Illegal SSIM XML response. See log files."
    print "===>", xml
    dom = parseString(xml)
    infos = dom.getElementsByTagName("sessionInfo")
    if len(infos) == 1:
        info = infos[0]
        sessionID = info.getAttribute('sessionID')
        domain_attr = info.getAttribute('domain')
        domain = "dc={0[0]},dc={0[1]},o=symc_ses".format(domain_attr.split('.'))
        session['%s sessionID' % address] = sessionID
        session['ldap'] = {address:{
            'domain':domain,
            'userDN':info.getAttribute('userDN'),
            'address':address,
            'login':login,
            'password':password,
            'domain_name': domain_attr
        }}
        l = get_ldap_connection(session, address)
    else:
        infos = dom.getElementsByTagName("status")
        if len(infos) == 1:
            raise DefaultDomainException, "%s" % (infos[0].getAttribute('errorMessage'),)
        else:
            raise DefaultDomainException, "Illegal SSIM response: %s" % (xml,)

def send_xml(address, path, session, xml):
    sessionID = session['%s sessionID' % address]
    print "SessionID:", sessionID
    if not sessionID:
        raise NoSessionIDException('Please authenticate')

    print "Send request to SSIM", address

    print "\n--------------------------\n",xml,"\n--------------------------\n"
    #initial value
    data = None

    conn = httplib.HTTPSConnection(address, timeout=10)
    conn.putrequest("POST", path)
    conn.putheader("content-type", "text/xml; charset=UTF-8")
    conn.putheader("Content-length", "%d" % len(xml))
    conn.endheaders()
    conn.send(xml)
    r1 = conn.getresponse()

    content_type = r1.getheader('content-type', None)
    data = r1.read()
    conn.close()
    
    return content_type, data

def distribute_config(address, session, agent_dn_list):
    path = '/sesa/servlet/Admin'
    sessionID = session['%s sessionID' % address]
    if not sessionID:
        raise NoSessionIDException('Please authenticate')

    xml_header = """<?xml version="1.0" encoding="UTF-8"?>
    <ssmcRequest requestID="1254922441483" sessionID="%s">
        <sendReloadConfigCommand>
            <computerList>\n"""

    xml = ""
    for agent in agent_dn_list:
        xml += "<computer>%s</computer>\n" % agent

    xml_footer = """
            </computerList>
        </sendReloadConfigCommand>
    </ssmcRequest>
    """

    xml = (xml_header % sessionID) + xml + xml_footer
    content_type, data = send_xml(address, path, session, xml)

    dom = parseString(data)
    status = dom.getElementsByTagName("status")

    if len(status) == 0 or status[0].getAttribute('success') != 'true':
        if ('ldap' in session.keys()) and (address in session['ldap']):
            params = session['ldap'][address]
            ldap_authenticate(session, address, params['login'], params['password'])
            #get new sessionID
            sessionID = session['%s sessionID' % address]
            #create xml with new sessionID
            xml = (xml_header % sessionID) + xml + xml_footer
            #send request again
            content_type, data = send_xml(address, path, session, xml, 1)
        else:
            raise NotAuthorisedException('Please authenticate')

def webapi_get_with_login(session, address, path, params = None, method = "POST", redirect = False):
    status, content_type, headers, cookies, data = webapi_get(session, address, path, params, method, redirect)

    if status == 302:
        status, content_type, headers, cookies, data = webapi_login(session, address)
        if status == 200:
            status, content_type, headers, cookies, data = webapi_get(session, address, path, params, method, redirect)
        else:
            log.error("Cannot login to " + address)
            
    return status, content_type, headers, cookies, data

def webapi_get(session, address, path, params = None, method = "POST", redirect = False):
    sessionID = session.get('%s WebAPI sessionID' % address)
    print "WebAPI SessionID:", sessionID

    Headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/xml"}

    if sessionID:
        Headers["Cookie"] = "JSESSIONID=%s" % sessionID

    if not params:
        params = {}
    else:
        params = urllib.urlencode(params, True)

    print "Send WebAPI request to SSIM", address

    print "\n-------Request Params-----\n",params,"\n--------------------------\n"
    #initial value
    data = None


    response = None
    request = None
    conn = None
    opener = None
    if redirect:
        url = 'https://' + address + path
        request = urllib2.Request(url)
        opener = urllib2.build_opener( openanything.SmartRedirectHandler() )
        response = opener.open(request)
    else:
        conn = httplib.HTTPSConnection(address, timeout=10)
        conn.request(method, path, params, Headers)
        response = conn.getresponse()

    cookies = cookie_processor.get_cookies( response )

    #store WebAPI session ID to current Django session
    new_session_id = cookies.get('JSESSIONID')
    if new_session_id:
        session['%s WebAPI sessionID' % address] = new_session_id

    content_type = response.getheader('content-type', None)
    data = response.read()

    if conn:
        conn.close()
    if opener:
        opener.close()

    return response.status, content_type, response.getheaders(), cookies, data

def webapi_login(session, address, login = None, password = None, domain = None):
    if not login:
        login = session['ldap'][address]['login']
    if not password:
        password = session['ldap'][address]['password']
    if not domain:
        domain = session['ldap'][address]['domain_name']

    #path = "/imr/ssim/ssim_login.htm"
    path = "/imr/config/api.jsp"
    params = {
        'cmd': 'LOGIN',
        'user': login,
        'pwd': password,
        'domain': domain,
    }
    status, content_type, headers, cookies, data = webapi_get(session, address, path, params)
        
    return status, content_type, headers, cookies, data
