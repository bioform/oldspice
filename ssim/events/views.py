from django.http import HttpResponse
from django.shortcuts import render_to_response

from symantec.ssim.utils import helper as utils
from symantec.ssim.utils import location
from symantec.ssim.utils import configuration

from symantec.ssim.exceptions import *
from django.shortcuts import redirect

from symantec.ssim.config.general import GeneralForm
from symantec.ssim.config import sensor
from symantec.ssim.config import agents
from symantec.ssim.config import general
from symantec.ssim.exceptions import *

def get_events(request, address):
    status, content_type, cookies, data = utils.webapi_get(request.session, '169.254.13.232', '/imr/config/api.jsp', {'cmd': 'EVENTS'})
    print "Status:", status, "Content-Type:", content_type,", Cookies:", cookies,", Data:", data
    return render_to_response('ssim/events/index.html', {'address':address},
        mimetype="text/html")