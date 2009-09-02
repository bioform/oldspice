from django.conf.urls.defaults import *

urlpatterns = patterns('symantec.ssim.views',
    (r'^$', 'index'),
    (r'^login/$', 'login'),
    (r'^ldap/$', 'test_ldap'),
)
