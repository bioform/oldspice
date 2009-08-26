from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_list
from symantec.machines.models import Machine
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.core import serializers

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
    # Create a machine based on what the user provided
    machine = Machine.objects.get(id=request.GET.get('id'))
    # Save the entry to the database
    machine.user_id = request.user.id
    machine.save()
    # Retrieve all the messages
    sort =  ("","-")[request.GET.get('dir')=='asc']
    sort += request.GET.get('sort', 'address')
    machine_list = Machine.objects.all().order_by(sort)
    # Serialize the result of the database retrieval to JSON and send an application/json response
    return HttpResponse(serializers.serialize('json', machine_list, indent=2, relations=('user',)),
            mimetype='application/json')

