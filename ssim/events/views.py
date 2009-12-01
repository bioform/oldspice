import xml.sax
from django.http import HttpResponse
from django.shortcuts import render_to_response
from symantec.ssim.utils import helper as utils
from django.shortcuts import redirect
from symantec.ssim.events.utils import queries
from symantec.ssim.events.utils import events_handler
from symantec.ssim.exceptions import *

def index(request, address):
    return render_to_response('ssim/events/index.html', {'address':address},
        mimetype="text/html")

def get_events(request, address):
    status, content_type, headers, cookies, data = utils.webapi_get(request.session, '169.254.13.232', '/imr/config/api.jsp', {'cmd': 'EVENTS'})
    print "Status:", status, "Content-Type:", content_type,", headers:", headers,", Cookies:", cookies,", Data:", data

    if status == 302:
        status, content_type, headers, cookies, data = utils.webapi_login(request.session, '169.254.13.232')
        print "Login status:", status, "Content-Type:", content_type,", headers:", headers,", Cookies:", cookies,", Data:", data
        if status == 200:
            status, content_type, headers, cookies, data = utils.webapi_get(request.session, '169.254.13.232', '/imr/config/api.jsp', {'cmd': 'EVENTS'})
            print "Good status:", status, "Content-Type:", content_type,", headers:", headers,", Cookies:", cookies,", Data:", data
        else:
            print "Error status:", status, "Content-Type:", content_type,", headers:", headers,", Cookies:", cookies,", Data:", data
            log.error("Cannot login to " + address)

    handler = events_handler.EventHandler()
    xml.sax.parseString(data, handler)

    return render_to_response('ssim/events/list.html', {'address':address},
        mimetype="text/html")

def get_queries(request, address):
    ldap_connection = utils.get_ldap_connection(request.session, address)
    ldap_info = request.session['ldap'][address]
    custom_queries = queries.get_custom_queries(ldap_connection, ldap_info['domain'])
    system_queries = queries.get_system_queries(ldap_connection, ldap_info['domain'])

    return render_to_response('ssim/events/queries.html', 
        {
            'address':address,
            'custom_queries':custom_queries,
            'system_queries':system_queries,
        },
        mimetype="text/html")