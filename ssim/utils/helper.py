import httplib
import ldap
import sys, os, traceback
from django.conf import settings
from datetime import datetime

def get_auth_xml(address, login, password):
    print "Try connect to SSIM", address
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <ssmcRequest requestID="1251719297259" sessionID="">
                    <login timeZoneID="GMT" domain="" clientip="" user="%s" password="%s">
                            <locale countryCode="RU" languageCode="ru" variant=""/>
                    </login>
    </ssmcRequest>
    """ % (login, password)
    print "\n--------------------------\n",xml,"\n--------------------------\n"
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