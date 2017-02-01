from django.conf.urls.defaults import *
from views import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('pujiahh.link.views',
    url(r'^(?P<lid>\d+)/$', Redirect),
)
