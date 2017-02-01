from django.conf.urls.defaults import *
from views import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('pujiahh.articles.views',
    (r'^(?P<aid>\d+)/$', article_detail),
    (r'^edit/(?P<subject>\w+)/(?P<aid>\d+)/$', article_edit),
    url(regex = r'^news/$',
        view  = news,
        name  = 'news',
    ),
    url(regex = r'^topics/$',
        view  = topics,
        name  = 'topics',
    ),
    url(regex = r'^submit/new/$',
        view  = SubmitNew.as_view(),
        name  = 'new_submit',
    ),
    url(regex = r'^submit/topic/$',
        view  = SubmitTopic.as_view(),
        name  = 'topic_submit',
    ),
)
