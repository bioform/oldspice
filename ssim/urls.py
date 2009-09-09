from django.conf.urls.defaults import *

urlpatterns = patterns('symantec.ssim.views',
    (r'^(?P<address>[^/]+)/login/$', 'login'),
    (r'^ldap/$', 'test_ldap'),
    (r'^(?P<address>[^/]+)$', 'index'),
)
