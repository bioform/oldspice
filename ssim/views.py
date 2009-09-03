from django.http import HttpResponse
from django import template
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy, ugettext as _
import ldap
from xml.dom.minidom import parse, parseString

from symantec.ssim.utils import helper as utils
from symantec.ssim.exceptions import *
from datetime import datetime


ERROR_MESSAGE = ugettext_lazy("Please enter a correct username and password. Note that both fields are case-sensitive.")
LOGIN_FORM_KEY = 'this_is_the_login_form'
root_path = None

def index(request):
    return HttpResponse('OK !', mimetype='text/plain')

def login(request):
    address  = request.GET.get('address','')
    # If this isn't already the login page, display it.
    if not request.POST.has_key(LOGIN_FORM_KEY):
        if request.POST:
            message = _("Please log in again, because your session has expired.")
        else:
            message = ""
        return display_login_form(request, message)


    try:
        ldap_authenticate(request)

        print "LDAP+address: ", request.session['ldap']

        return render_to_response('ssim/index.html', {'current_date': datetime.now()})
    
    except ldap.INVALID_CREDENTIALS:
        message = ERROR_MESSAGE
    except ldap.LDAPError as ex:
        message = "LDAP error type \"%s\". Arguments \"%s\". Message: " % (type(ex), ex.args, ex)
    except DefaultDomainException as ex:
        message = ex.__str__()

    return render_to_response('ssim/login.html', {'current_date': datetime.now()})

def test_ldap(request):
    # Serialize the result of the database retrieval to JSON and send an application/json response
    try:
        data = utils.get_ldap_connection(request);
    except ldap.INVALID_CREDENTIALS:
        data = "Your username or password is incorrect."
    except ldap.LDAPError as ex:
        data = "LDAP error type \"%s\". Arguments \"%s\". Message: " % (type(ex), ex.args, ex)
    return HttpResponse(data,
            mimetype='text/plain')

def display_login_form(request, error_message='', extra_context=None):
    request.session.set_test_cookie()
    context = {
        'title': _('Log in'),
        'app_path': request.get_full_path(),
        'error_message': error_message,
        'root_path': root_path,
    }
    context.update(extra_context or {})
    context_instance = template.RequestContext(request)
    return render_to_response('ssim/login.html', context,
        context_instance=context_instance
    )

def ldap_authenticate(request):
    address  = request.POST.get('address')
    login    = request.POST.get('username')
    password = request.POST.get('password')
    # Serialize the result of the database retrieval to JSON and send an application/json response
    xml = utils.get_auth_xml(address,login,password);
    dom = parseString(xml)
    infos = dom.getElementsByTagName("sessionInfo")
    if len(infos) == 1:
        info = infos[0]
        domain = "dc={0[0]},dc={0[1]},o=symc_ses".format(info.getAttribute('domain').split('.'))
        request.session['ldap'] = {address:{
            'domain':domain,
            'userDN':info.getAttribute('userDN'),
            'address':address,
            'login':login,
            'password':password,
        }}
        l = utils.get_ldap_connection(request.session, address)
    else:
        raise DefaultDomainException, "Illegal SSIM response: %s" % (xml,)