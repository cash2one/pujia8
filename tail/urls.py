from django.conf.urls.defaults import *
from views import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('pujiahh.checkin.views',
    url(r'^add/$', add_tail),
)
