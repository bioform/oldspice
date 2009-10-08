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
    utils.webapi_get(request.session, '169.254.13.232', '/imr/config/api.jsp', {'cmd': 'EVENTS'})
    return HttpResponse('OK!',
            mimetype='text/plain')