from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    (r'^$', Request),
    (r'^send/$', send),
    (r'^(?P<rid>\d+)/$', show),
    (r'^(?P<rid>\d+)/(?P<votetype>\w+)/$', vote),
)
