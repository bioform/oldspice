from django.conf.urls.defaults import *

urlpatterns = patterns('symantec.ssim.events.views',
    (r'^(?P<address>[^/]+)/$', 'index'),
    (r'^(?P<address>[^/]+)/events$', 'get_events'),
    (r'^(?P<address>[^/]+)/event/(?P<guid>[^/]+)$', 'get_event'),
    (r'^(?P<address>[^/]+)/event_stats$', 'get_event_stats'),
    (r'^(?P<address>[^/]+)/queries$', 'get_query_groups'),
)