from django.conf.urls.defaults import *

urlpatterns = patterns('symantec.ssim.events.views',
    (r'^(?P<address>[^/]+)/$', 'get_events'),
)