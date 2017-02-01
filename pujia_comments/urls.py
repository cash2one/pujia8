from django.conf.urls import patterns, include, url
from views import *

urlpatterns = patterns('',
    url(r'^post/$', post_comment, name='post_comment'),
    url(r'^delete/(?P<cid>\d+)/$', delete_comment, name='delete_comment'),
    url(r'^hot/(?P<cid>\d+)/$', hot_comment, name='hot_comment'),
    url(r'^like/(?P<cid>\d+)/$', add_positive, name='add_positive'),
    url(r'^hotlist/$', hot_comments_list, name='hot_comments_list'),
    url(r'^edit/(?P<cid>\d+)/$', edit_comment, name='edit_comment'),
)
