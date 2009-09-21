from django.conf.urls.defaults import *
from django.contrib import admin
from symantec.authuser.models import *
from symantec.authuser.admin import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^symantec/', include('symantec.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^machines/', include('symantec.machines.urls')),
    (r'^ssim/', include('symantec.ssim.urls')),
    (r'^ssim/config/', include('symantec.ssim.config.urls')),
    (r'^$', include('symantec.machines.urls')),
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'authuser/login.html'}),
    (r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT+'/css'}),
    (r'^img/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT+'/img'}),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT+'/js'})
)
