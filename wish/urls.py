from django.conf.urls.defaults import *
from views import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('pujiahh.wish.views',
    (r'^(?P<wid>\d+)/$', wish_detail),
    (r'^(?P<slug>\w+)/$', wish_detail_slug),
)
