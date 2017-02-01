from django.conf.urls.defaults import *
from views import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('pujiahh.weixin.views',
    url(r'^$', handleRequest),
    url(r'^creatmenu/$', creatmenu),
    url(r'^test/$', handleRequestTest),
)
