from django.http import HttpResponse
from django import template
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy, ugettext as _
import ldap
from xml.dom.minidom import parse, parseString

from symantec.ssim.utils import helper as utils
from symantec.ssim.utils import location
from symantec.ssim.utils import product
from symantec.ssim.utils import configuration

from symantec.ssim.exceptions import *
from datetime import datetime
from django.shortcuts import redirect
import sys


ERROR_MESSAGE = ugettext_lazy("Please enter a correct username and password. Note that both fields are case-sensitive.")
LOGIN_FORM_KEY = 'this_is_the_login_form'
root_path = None

def index(request, address = None):
    ldap_connection = None
    try:
        ldap_connection = utils.get_ldap_connection(request.session, address)
    except Exception, err:
        log.info("Cannot connect to LDAP " + address + ". " + str(err))
    if ldap_connection == None:
        return redirect('symantec.ssim.views.login', address=address)

    return render_to_response('ssim/index.html', {'address':address},
        mimetype="text/html")

def locations(request, address):
    ldap_connection = utils.get_ldap_connection(request.session, address)
    ldap_info = request.session['ldap'][address]
    clients = location.all(ldap_connection, ldap_info['domain'])

    return render_to_response('ssim/locations.html', {'clients':clients, 'address':address},
        mimetype="text/html")

def products(request, address, client = None):
    ldap_connection = utils.get_ldap_connection(request.session, address)
    if ldap_connection is None:
        return HttpResponse("Please reconnect to SSIM", mimetype='text/plain')
    ldap_info = request.session['ldap'][address]
    product_list= product.all(ldap_connection, ldap_info['domain'])
    return render_to_response('ssim/products.html', {'products':product_list, 'address':address},
        mimetype="text/html")

def config_by_product_id(request, address, productID, message = None):
    ldap_connection = utils.get_ldap_connection(request.session, address)
    ldap_info = request.session['ldap'][address]
    (product_instance, config_root, config_list) = configuration.configurations(ldap_connection, ldap_info['domain'], productID)
    return render_to_response('ssim/configurations.html', {'product':product_instance,'config_root':config_root, 'configurations':config_list, 'address':address},
        mimetype="text/html")

def client_products(request, address, client = None):
    ldap_connection = utils.get_ldap_connection(request.session, address)
    locationDN = request.POST.get('locationDN', None)
    if locationDN == None:
        ldap_info = request.session['ldap'][address]
        locationDN = location.client_dn(ldap_connection, ldap_info['domain'], client)
    products = product.client_products(ldap_connection, locationDN)
    return render_to_response('ssim/client_products.html', {'products':products, 'address':address},
        mimetype="text/html")


def create_config(request, address, productID, config_name):
    try:
        ldap_connection = utils.get_ldap_connection(request.session, address)
        ldap_info = request.session['ldap'][address]
        new_config_name = config_name.encode("utf-8")
        result = configuration.copy_dafault_config(ldap_connection, ldap_info['domain'], productID, new_config_name)
    except Exception as ex:
        return config_by_product_id(request, address, productID, ex)

    return config_by_product_id(request, address, productID)

def login(request, address):
    # If this isn't already the login page, display it.
    if not request.POST.has_key(LOGIN_FORM_KEY):
        if request.POST:
            message = _("Please log in again, because your session has expired.")
        else:
            message = ""
        return display_login_form(request, error_message=message, address=address)


    try:
        address = request.POST.get('address')
        login    = request.POST.get('username')
        ldap_authenticate(request)

        print "LDAP+address: ", request.session['ldap']

        return redirect("/ssim/%s" % address)
    
    except ldap.INVALID_CREDENTIALS:
        message = ERROR_MESSAGE
    except ldap.LDAPError as (ex):
        message = "LDAP error type \"%s\". Arguments \"%s\". Message: %s" % (type(ex), ex.args, ex)
    except DefaultDomainException as ex:
        message = ex.__str__()
    return display_login_form(request, error_message=message, address=address)

def test_ldap(request):
    # Serialize the result of the database retrieval to JSON and send an application/json response
    try:
        data = utils.get_ldap_connection(request);
    except ldap.INVALID_CREDENTIALS:
        data = "Your username or password is incorrect."
    except ldap.LDAPError as ex:
        data = "LDAP error type \"%s\". Arguments \"%s\". Message: %s" % (type(ex), ex.args, ex)
    return HttpResponse(data,
            mimetype='text/plain')

def display_login_form(request, error_message='', extra_context=None, address=''):
    request.session.set_test_cookie()
    context = {
        'title': _('Log in'),
        'app_path': request.get_full_path(),
        'error_message': error_message,
        'root_path': root_path,
        'address':  address,
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
    utils.ldap_authenticate(request.session, address, login, password)
