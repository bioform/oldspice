from django.conf.urls.defaults import *

urlpatterns = patterns('symantec.ssim.events.views',
    (r'^(?P<address>[^/]+)/$', 'index'),
    (r'^(?P<address>[^/]+)/events$', 'get_events'),
    (r'^(?P<address>[^/]+)/queries$', 'get_queries'),
)