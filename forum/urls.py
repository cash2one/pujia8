from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

from forum import views

urlpatterns = patterns('',
    url(r'^$', views.recent, name='lbforum_recent'),
    url(r'^forum/(?P<forum_slug>\w+)/$', views.forum, name='lbforum_forum'),
    url(r'^forum/(?P<forum_slug>\w+)/(?P<topic_type>\w+)/$', views.forum, name='lbforum_forum'),
    url(r'^forum/(?P<forum_slug>\w+)/(?P<topic_type>\w+)/(?P<topic_type2>\w+)/$',
        views.forum, name='lbforum_forum'),

    url('^topic/(?P<topic_id>\d+)/$', views.topic, name='lbforum_topic'),
    url('^topic/(?P<topic_id>\d+)/fav/$', views.seed, name='lbforum_topic_fav'),
    url('^topic/(?P<topic_id>\d+)/delete/$', views.delete_topic, name='lbforum_delete_topic'),
    url('^topic/(?P<topic_id>\d+)/update_topic_attr_as_not/(?P<attr>\w+)/$',
        views.update_topic_attr_as_not, name='lbforum_update_topic_attr_as_not'),

    url('^topic/new/(?P<forum_id>\d+)/$', views.new_post, name='lbforum_new_topic'),
    url('^reply/new/(?P<topic_id>\d+)/$', views.new_post, name='lbforum_new_replay'),

    url('^post/(?P<post_id>\d+)/$', views.post, name='lbforum_post'),
    url('^post/(?P<post_id>\d+)/edit/$', views.edit_post, name='lbforum_post_edit'),
    url('^post/(?P<post_id>\d+)/delete/$', views.delete_post, name='lbforum_post_delete'),
    url('^score/(?P<post_id>\d+)/$', views.score, name='lbforum_post_score'),

    url('^user/(?P<user_id>\d+)/topics/$', views.user_topics, name='lbforum_user_topics'),
    url('^user/(?P<user_id>\d+)/posts/$', views.user_posts, name='lbforum_user_posts'),
    url('^user/(?P<user_id>\d+)/at/$', views.user_at, name='lbforum_user_at'),
    url('^user/(?P<user_id>\d+)/fav/$', views.user_seeds, name='lbforum_user_favs'),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './static'}),
    (r'^upload/$', views.upload),
    (r'^search/$', views.search),
    (r'^robots.txt', views.robots),
    (r'^crontab/$', views.crontab),
    (r'^crontab_month/$', views.crontab_month),
    (r'^crontab_week/$', views.crontab_week),
)

