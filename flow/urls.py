from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    url(r'^$', news_index, name='news_index'),
    url(r'^(?P<fid>\d+)/$', news_info, name='news_info'),
    url(r'^verify/$', verify, name='verify'),
    url(r'^spider/bili/$', spider_Bili, name='spider_Bili'),
    url(r'^spider/(?P<type>\w+)/$', spider, name='spider'),
    url(r'^(?P<column>\w+)/$', news_column, name='news_column'),
)
