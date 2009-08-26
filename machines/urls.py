from django.conf.urls.defaults import *

urlpatterns = patterns('symantec.machines.views',
    (r'^$', 'index'),
    (r'^take/$', 'take'),
)
