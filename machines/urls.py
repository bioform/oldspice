from django.conf.urls.defaults import *

urlpatterns = patterns('symantec.machines.views',
    (r'^$', 'index'),
    (r'^take/$', 'take'),
    (r'^commenting/$', 'update_comment'),
    (r'^version/$', 'get_version'),
)
