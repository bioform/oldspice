from django.conf.urls.defaults import *

urlpatterns = patterns('symantec.ssim.config.views',
    (r'^(?P<address>[^/]+)/product/(?P<productID>\d+)/config/(?P<config_name>[^/]+)/distribute$', 'distribute_config'),
    (r'^(?P<address>[^/]+)/product/(?P<productID>\d+)/config/(?P<config_name>.+)/agents-tab$', 'config_agents'),
    (r'^(?P<address>[^/]+)/product/(?P<productID>\d+)/config/(?P<config_name>.+)/general-tab$', 'config_general'),
    (r'^(?P<address>[^/]+)/product/(?P<productID>\d+)/config/(?P<config_name>.+)/options-tab$', 'config_options'),
    (r'^(?P<address>[^/]+)/product/(?P<productID>\d+)/config/(?P<config_name>.+)/filter-tab$', 'config_filter'),
    (r'^(?P<address>[^/]+)/product/(?P<productID>\d+)/config/(?P<config_name>.+)/aggregator-tab$', 'config_aggregator'),
    (r'^(?P<address>[^/]+)/product/(?P<productID>\d+)/config/(?P<config_name>.+)/sensor-tab$', 'sensor_tab'),
    (r'^(?P<address>[^/]+)/product/(?P<productID>\d+)/config/(?P<config_name>.+)/sensors/(?P<selected_sensor>.*)$', 'config_sensors'),
    (r'^(?P<address>[^/]+)/product/(?P<productID>\d+)/config/(?P<config_name>.+)/sensor/(?P<sensor_name>[^/]*)$', 'config_sensor'),
    (r'^(?P<address>[^/]+)/product/(?P<productID>\d+)/config/(?P<config_name>.+)/sensor/(?P<sensor_name>[^/]+)/delete$', 'delete_sensor'),
    (r'^(?P<address>[^/]+)/product/(?P<productID>\d+)/config/(?P<config_name>.+)/sensor/(?P<sensor_name>[^/]+)/change-status$', 'change_sensor_status'),
    (r'^(?P<address>[^/]+)/product/(?P<productID>\d+)/config/(?P<config_name>[^/]+)/$', 'config_by_name'),
)