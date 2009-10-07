import httplib
import ldap
import sys, os, traceback
from django.conf import settings
from datetime import datetime
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
    try:
        conn.putrequest("POST", "/sesa/servlet/Admin")
        conn.putheader("Content-type", "text/xml; charset=UTF-8")
        conn.putheader("Content-length", "%d" % len(xml))
        conn.endheaders()
        conn.send(xml)
        r1 = conn.getresponse()
        data1 = r1.read()
        conn.close()
    except Exception:
        print "Unexpected error:", sys.exc_info()[0]
        traceback.print_exc()
        data1 = ""
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
    xml = get_auth_xml(address,login,password);
    if len(xml) == 0:
        raise DefaultDomainException, "Illegal SSIM XML response. See log files."
    print "===>", xml
    dom = parseString(xml)
    infos = dom.getElementsByTagName("sessionInfo")
    if len(infos) == 1:
        info = infos[0]
        sessionID = info.getAttribute('sessionID')
        domain = "dc={0[0]},dc={0[1]},o=symc_ses".format(info.getAttribute('domain').split('.'))
        session['%s sessionID' % address] = sessionID
        session['ldap'] = {address:{
            'domain':domain,
            'userDN':info.getAttribute('userDN'),
            'address':address,
            'login':login,
            'password':password,
        }}
        l = get_ldap_connection(session, address)
    else:
        infos = dom.getElementsByTagName("status")
        if len(infos) == 1:
            raise DefaultDomainException, "%s" % (infos[0].getAttribute('errorMessage'),)
        else:
            raise DefaultDomainException, "Illegal SSIM response: %s" % (xml,)

def send_xml(address, path, session, xml, iteration = 0):
    sessionID = session['%s sessionID' % address]
    if not sessionID:
        raise NoSessionIDException('Please authenticate')

    print "Send request to SSIM", address,", iteration:", iteration

    print "\n--------------------------\n",xml,"\n--------------------------\n"
    #initial value
    data = None

    conn = httplib.HTTPSConnection(address, timeout=10)
    conn.putrequest("POST", path)
    conn.putheader("Content-type", "text/xml; charset=UTF-8")
    conn.putheader("Content-length", "%d" % len(xml))
    conn.endheaders()
    conn.send(xml)
    r1 = conn.getresponse()
    print "Response headers:", r1.getheaders()
    content_type = r1.getheader('Content-type', None)
    
    if content_type == 'text/xml':
        data = r1.read()
        conn.close()
    else:
        if iteration == 0 and ('ldap' in session.keys()) and (address in session['ldap']):
            params = session['ldap'][address]
            ldap_authenticate(session, address, params['login'], params['password'])
            data = send_xml(address, path, session, xml, 1)
        else:
            raise NotAuthorisedException('Please authenticate')

    return data

def distribute_config(address, session, agent_dn_list):
    sessionID = session['%s sessionID' % address]
    if not sessionID:
        raise NoSessionIDException('Please authenticate')

    xml_header = """<?xml version="1.0" encoding="UTF-8"?>
    <ssmcRequest requestID="1254922441483" sessionID="%s">
        <sendReloadConfigCommand>
            <computerList>
    """ % (sessionID)

    for agent in agent_dn_list:
        xml_header += "<computer>%s</computer>" % agent
    xml_footer = """
            </computerList>
        </sendReloadConfigCommand>
    </ssmcRequest>
    """

    xml = xml_header + xml_footer
    send_xml(address, '/sesa/servlet/Admin', session, xml)