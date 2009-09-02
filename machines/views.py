from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_list

from symantec.machines.models import Machine
import symantec.machines.utils.helper as utils

from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.core import serializers
from django.core.mail import send_mail
import threading
import httplib
from datetime import datetime
import sys, os, traceback

@login_required
def index(request):
    sort =  ("","-")[request.GET.get('dir')=='asc']
    sort += request.GET.get('sort', 'address')
    machine_list = Machine.objects.all().order_by(sort)
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    
    return object_list(request,queryset=machine_list, template_name='machines/index.html',
        paginate_by=20, page=page)

def take(request):
    # Get a machine based on what the user provided
    machine = Machine.objects.get(id=request.GET.get('id'))
    # Save the entry to the database
    previous_user = machine.user
    machine.user_id = request.user.id
    machine.save()
    #send notification
    notify(machine, request.user, previous_user)
    # Retrieve all the messages
    sort =  ("","-")[request.GET.get('dir')=='asc']
    sort += request.GET.get('sort', 'address')
    machine_list = Machine.objects.all().order_by(sort)
    # Serialize the result of the database retrieval to JSON and send an application/json response
    return HttpResponse(serializers.serialize('json', machine_list, indent=2, relations=('user',)),
            mimetype='application/json')

def get_version(request):
    machine = Machine.objects.get(id=request.GET.get('id'))

    upddate_delta = datetime.now() - machine.updated_at
    if upddate_delta.seconds > 60*3:
        machine_info = update_ssim_info(machine)
    else:
        machine_info = machine.info

    return HttpResponse(machine_info, mimetype='text/html')

def update_ssim_info(machine):
    print "Try to load SSIM information for", machine.address
    data1 = ""
    conn = httplib.HTTPSConnection(machine.address, timeout=10)
    try:
        conn.connect()
        conn.request("GET", "/imr/admin/ssimhistory.jsp")
        r1 = conn.getresponse()
        #check another URL
        if r1.status == 404:
            #print r1.status, r1.reason
            conn.close()
            conn.request("GET", "/imr/config/ssimhistory.jsp")
            r1 = conn.getresponse()
        data1 = r1.read()
        conn.close()
    except Exception:
        print "Unexpected error while getting SSIM info:", sys.exc_info()[0]
        #traceback.print_exc()
    if len(data1) != 0:
        data1 = utils.text(data1)

    machine.info = data1
    machine.save()
    return data1
    return ""



def notify(machine, user, previous_user):
    # Format our information here, in the main thread
    subject = "Machine %s was taked by another user" % machine.name
    message = """
        User %s %s take machine %s.
    """ % (user.first_name, user.last_name, machine.address)
    recipients = [previous_user.email]
    from_email = 'symantec@bridge-quest.com'
    # Create a new thread in Daemon mode to send message
    t = threading.Thread(target=send_mail,
                         args=[subject, message, from_email, recipients],
                         kwargs={'fail_silently': True})
    t.setDaemon(True)
    t.start()

