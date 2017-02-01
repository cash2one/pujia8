from django.conf.urls.defaults import *
from views import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^register/$', register),
    url(r'^login/$', login),
    url(r'^logout/$', logout),
    url(r'^change/avatar/$', change_avatar),
    url(r'^change/background/$', change_background),
    url(r'^change/background/save/$', change_background_save),
    url(r'^change/introduce/$', change_introduce),
    url(r'^change/password/$', change_password),
    url(r'^password_reset/$', 
        'django.contrib.auth.views.password_reset', 
        {'post_reset_redirect' : '/account/password_reset/mailed/'},
        name="password_reset"),
    url(r'^password_reset/mailed/$',
        'django.contrib.auth.views.password_reset_done'),
    url(r'^password_reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm', 
        {'post_reset_redirect' : '/account/password_reset/complete/'}),
    url(r'^password_reset/complete/$', 
        'django.contrib.auth.views.password_reset_complete'),
)
