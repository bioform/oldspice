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
from symantec.ssim.config import agents
from symantec.ssim.config import general

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

    if request.method == 'GET':
        data = {'name':config.name,
                'desc':config.desc,
                'updated_at':config.updated_at,
                'configDN':config.dn
               }
        form = GeneralForm(initial = data)
    else:
        form = GeneralForm(request.POST)
        if form.is_valid():
            # save data
            general.update_config(ldap_connection, config, form)

    return render_to_response('ssim/config/general.html', {
        'productID':productID,
        'config':config,
        'form':form,
        'address':address,
        'action':request.path},
        mimetype="text/html")

def config_filter(request, address, productID, config_name):
    pass

def config_aggregator(request, address, productID, config_name):
    pass

def sensor_tab(request, address, productID, config_name,):
    return render_to_response('ssim/config/sensor-tab.html', {'productID':productID, 'config_name':config_name, 'address':address},
        mimetype="text/html")

def delete_sensor(request, address, productID, config_name, sensor_name):
    ldap_connection = utils.get_ldap_connection(request.session, address)

    configDN = request.POST.get('configDN', None)
    config = None;
    if configDN == None:
        ldap_info = request.session['ldap'][address]
        (product_instance, config_root, config) = configuration.get_config_by_name(ldap_connection, ldap_info['domain'], productID, config_name)
    else:
        config = configuration.get_config_by_dn(ldap_connection, configDN)

    sensor_config = configuration.get_sensor_config(ldap_connection, config)
    sensor_xml = sensor.remove_sensor_from_xml(sensor_config.data, sensor_name)
    # save data
    configuration.update_settings(ldap_connection, sensor_config.dn, sensor_xml)
    
    return redirect("/ssim/config/%s/product/%s/config/%s/sensors/" %
        (address, productID, config_name))

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

    #check that sensor_name is specified
    if not sensor_name or len(sensor_name) == 0:
        sensor_name = None

    #create dynamic form !!!
    form_clazz = sensor.get_sensor_form(sensor_config.data, sensor_name = sensor_name)
    sensor_instance = form_clazz.sensor
    # check request method
    form = None
    refresh_sensor_list = False
    is_sensor_saved = False
    if request.method == 'GET':
        form = form_clazz()
    elif request.method == 'POST':
        form = form_clazz(request.POST)
        if form.is_valid():
            saved_sensor_name, sensor_xml = form.update_xml()
            # save data
            configuration.update_settings(ldap_connection, sensor_config.dn, sensor_xml)
            is_sensor_saved = True
            if not sensor_name:
                sensor_name = saved_sensor_name
                refresh_sensor_list = True

    return render_to_response('ssim/config/sensor.html', {'productID':productID, 
        'config':config,
        'sensor':sensor_instance,
        'form':form,
        'address':address,
        'action':request.path,
        'update_item_list':refresh_sensor_list,
        'sensor_saved':is_sensor_saved},
        mimetype="text/html")

def change_sensor_status(request, address, productID, config_name, sensor_name):
    try:
        ldap_connection = utils.get_ldap_connection(request.session, address)

        configDN = request.POST.get('configDN', None)
        config = None;
        if configDN == None:
            ldap_info = request.session['ldap'][address]
            (product_instance, config_root, config) = configuration.get_config_by_name(ldap_connection, ldap_info['domain'], productID, config_name)
        else:
            config = configuration.get_config_by_dn(ldap_connection, configDN)

        sensor_config = configuration.get_sensor_config(ldap_connection, config)
        status, sensor_xml = sensor.change_status(sensor_config.data, sensor_name)
        # save data
        configuration.update_settings(ldap_connection, sensor_config.dn, sensor_xml)
    except Exception as ex:
        status = ex
    return HttpResponse(status,
            mimetype='text/plain')

def config_sensors(request, address, productID, config_name, selected_sensor):
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

    #define selected and first link
    first_sensor = None
    if len(sensor_list) > 0:
        first_sensor = sensor_list[0].name
    # render
    return render_to_response('ssim/config/sensors.html', {
                'productID':productID,
                'config':config,
                'sensor_config': sensor_config,
                'sensors':sensor_list,
                'first_link':first_sensor,
                'selected_link':selected_sensor,
                'address':address,
                },
                mimetype="text/html")

def config_options(request, address, productID, config_name):
    pass

def config_agents(request, address, productID, config_name):
    ldap_connection = utils.get_ldap_connection(request.session, address)

    configDN = request.POST.get('configDN', None)
    config = None;
    if configDN == None:
        ldap_info = request.session['ldap'][address]
        (product_instance, config_root, config) = configuration.get_config_by_name(ldap_connection, ldap_info['domain'], productID, config_name)
    else:
        config = configuration.get_config_by_dn(ldap_connection, configDN)

    #save data
    if request.method == 'POST':
        agents.save(ldap_connection, config, request.POST.getlist('agents'))

    #get all agents and agents references
    ldap_info = request.session['ldap'][address]
    all_agents = location.all(ldap_connection, ldap_info['domain'])
    linked_agents = location.all(ldap_connection, ldap_info['domain'], config.elements_names)
    
    return render_to_response('ssim/config/agents-tab.html', {'productID':productID,
        'config':config,
        'all_agents': all_agents,
        'agents': linked_agents,
        'address': address,
        'action':request.path},
        mimetype="text/html")