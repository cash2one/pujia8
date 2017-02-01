from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from views import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('pujiahh.checkin.views',
    url(r'^$', login_required(check_in)),
)
