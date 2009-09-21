from django.conf.urls.defaults import *

urlpatterns = patterns('symantec.ssim.views',
    (r'^(?P<address>[^/]+)/login/$', 'login'),
    (r'^(?P<address>[^/]+)/locations$', 'locations'),
    (r'^(?P<address>[^/]+)/products$', 'products'),
    (r'^(?P<address>[^/]+)/product/(?P<productID>\d+)$', 'config_by_product_id'),
    (r'^(?P<address>[^/]+)/products/(?P<client>[^/]+)$', 'client_products'),
    (r'^ldap/$', 'test_ldap'),
    (r'^(?P<address>[^/]+)$', 'index'),
)
