from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('pujiahh.gifts.views',
    (r'^$', list),
    (r'^exchange/(?P<gift_id>\d+)/$', exchange),
)
