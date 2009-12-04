import xml.sax
from django.http import HttpResponse
from django.shortcuts import render_to_response
from symantec.ssim.utils import helper as utils
from django.shortcuts import redirect

from symantec.ssim.events.utils import queries
from symantec.ssim.events.utils import converter
from symantec.ssim.events.utils import events_handler
from symantec.ssim.events.utils.queries import Query

from symantec.ssim.exceptions import *
from symantec.ssim.events.meta.field import DEFAULT_FIELD_LIST

def index(request, address):
    user_agent = request.META['HTTP_USER_AGENT']
    print "User Agent:", user_agent
    
    browser = 'chrome'
    if user_agent.find('MSIE') != -1:
        browser = 'ie'
    elif user_agent.find('Firefox') != -1:
        browser = 'firefox'

    return render_to_response('ssim/events/index.html', {
            'address':address,
            'browser': browser,
        },
        mimetype="text/html")

def get_events(request, address):
    request_data = request.POST
    if request.method == 'GET':
        request_data = request.GET
    params = {'cmd': 'EVENTS'}
    query = converter.create_query(request_data)
    obj_per_page = request_data.get('obj_per_page', "25")

    if query:
        params['nPerPage'] = obj_per_page
        #add conditions
        filter = converter.query_for_archive(query)
        if filter:
            params['filter'] = filter
            print "---> filter:", params['filter']

    status, content_type, headers, cookies, data = utils.webapi_get(request.session, '169.254.13.232', '/imr/config/api.jsp', params)

    if status == 302:
        status, content_type, headers, cookies, data = utils.webapi_login(request.session, '169.254.13.232')
        if status == 200:
            status, content_type, headers, cookies, data = utils.webapi_get(request.session, '169.254.13.232', '/imr/config/api.jsp', params)
        else:
            log.error("Cannot login to " + address)

    handler = events_handler.EventHandler()
    xml.sax.parseString(data, handler)

    return render_to_response('ssim/events/list.html', {
            'address':address,
            'events': handler.events,
            'fields': DEFAULT_FIELD_LIST,
            'obj_per_page': obj_per_page
        },
        mimetype="text/html")

def get_query_groups(request, address):
    ldap_connection = utils.get_ldap_connection(request.session, address)
    ldap_info = request.session['ldap'][address]

    query_groups = queries.get_query_groups(ldap_connection, ldap_info['domain'])
    system_query_groups = queries.get_system_query_groups(ldap_connection, ldap_info['domain'])

    return render_to_response('ssim/events/query_groups.html',
        {
            'address':address,
            'query_groups':query_groups,
            'system_query_groups':system_query_groups,
        },
        mimetype="text/html")
