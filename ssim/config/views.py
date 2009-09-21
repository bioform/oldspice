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

from symantec.ssim.config.general import GeneralForm
from symantec.ssim.config import sensor

def index(request, address = None):

    ldap_connection = utils.get_ldap_connection(request.session, address)
    if ldap_connection == None:
        return redirect('symantec.ssim.views.login', address=address)

    return render_to_response('ssim/index.html', {'address':address},
        mimetype="text/html")

def config_by_name(request, address, productID, config_name):
    ldap_connection = utils.get_ldap_connection(request.session, address)
    ldap_info = request.session['ldap'][address]
    (product_instance, config_root, config) = configuration.get_config_by_name(ldap_connection, ldap_info['domain'], productID, config_name)
        
    return render_to_response('ssim/config/edit.html', {'product':product_instance, 'config':config, 'address':address},
        mimetype="text/html")

def config_general(request, address, productID, config_name):
    ldap_connection = utils.get_ldap_connection(request.session, address)

    configDN = request.POST.get('configDN', None)
    config = None;
    if configDN == None:
        ldap_info = request.session['ldap'][address]
        (product_instance, config_root, config) = configuration.get_config_by_name(ldap_connection, ldap_info['domain'], productID, config_name)
    else:
        config = configuration.get_config_by_dn(ldap_connection, configDN)

    data = {'name':config.name,
            'desc':config.desc,
            'updated_at':config.updated_at,
            'configDN':config.dn}
    general_form = GeneralForm(initial = data)
    return render_to_response('ssim/config/general.html', {'productID':productID, 'config':config, 'form':general_form,'address':address},
        mimetype="text/html")

def config_filter(request, address, productID, config_name):
    pass

def config_aggregator(request, address, productID, config_name):
    pass

def sensor_tab(request, address, productID, config_name,):
    return render_to_response('ssim/config/sensor-tab.html', {'productID':productID, 'config_name':config_name, 'address':address},
        mimetype="text/html")

def config_sensor(request, address, productID, config_name, sensor_name):
    ldap_connection = utils.get_ldap_connection(request.session, address)
    
    configDN = request.POST.get('configDN', None)
    config = None;
    if configDN == None:
        ldap_info = request.session['ldap'][address]
        (product_instance, config_root, config) = configuration.get_config_by_name(ldap_connection, ldap_info['domain'], productID, config_name)
    else:
        config = configuration.get_config_by_dn(ldap_connection, configDN)

    sensor_config = configuration.get_sensor_config(ldap_connection, config)

    #create dynamic form !!!
    form_clazz = sensor.get_sensor_form(sensor_config.data, sensor_name = sensor_name)
    sensor_instance = form_clazz.sensor
    form = form_clazz()
    return render_to_response('ssim/config/sensor.html', {'productID':productID, 'config':config, 'sensor':sensor_instance, 'form':form,'address':address},
        mimetype="text/html")

def config_sensors(request, address, productID, config_name):
    ldap_connection = utils.get_ldap_connection(request.session, address)

    configDN = request.POST.get('configDN', None)
    config = None;
    if configDN == None:
        ldap_info = request.session['ldap'][address]
        (product_instance, config_root, config) = configuration.get_config_by_name(ldap_connection, ldap_info['domain'], productID, config_name)
    else:
        config = configuration.get_config_by_dn(ldap_connection, configDN)

    sensor_config = configuration.get_sensor_config(ldap_connection, config)
    sensor_list = sensor.get_all_sensors(sensor_config.data)
    selected_sensor = None
    if len(sensor_list) > 0:
        selected_sensor = sensor_list[0].name
    return render_to_response('ssim/config/sensors.html', {
                'productID':productID,
                'config':config,
                'sensors':sensor_list,
                'selected_link':selected_sensor,
                'address':address,
                },
                mimetype="text/html")

def config_options(request, address, productID, config_name):
    pass