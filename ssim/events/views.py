from django.http import HttpResponse
from django.shortcuts import render_to_response
from symantec.ssim.utils import helper as utils
from django.shortcuts import redirect
from symantec.ssim.events.utils import queries
from symantec.ssim.exceptions import *

def get_events(request, address):
    status, content_type, cookies, data = utils.webapi_get(request.session, '169.254.13.232', '/imr/config/api.jsp', {'cmd': 'EVENTS'})
    print "Status:", status, "Content-Type:", content_type,", Cookies:", cookies,", Data:", data
    return render_to_response('ssim/events/index.html', {'address':address},
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