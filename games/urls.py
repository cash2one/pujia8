from django.conf.urls.defaults import *
from views import *
from models import Games
from tagging.views import tagged_object_list

urlpatterns = patterns('pujiahh.games.views',
    (r'^wandoujia/$', wandoujia),
    (r'^category/(?P<cate>\w+)/$', category),
    (r'^edit/(?P<gid>\d+)/$', game_edit),
    url(r'^(?P<gid>\d+)/$', detail, name = 'game_detail'),
    url(r'^qiuhanhua/(?P<game_id>\d+)/$', qiuhanhua, name = 'qiuhanhua'),
    url(r'^score/(?P<game_id>\d+)/$', gamescore, name = 'gamescore'),
    (r'^(?P<platform>[^/]+)/tag/(?P<game_tag>[^/]+)/$', games_by_tag),
    url(regex = r'^$',
        view  = games_list,
        name  = 'games_list',
    ),
    url(regex = r'^times/$',
        view  = games_by_time,
        name  = 'games_by_time',
    ),
    url(regex = r'^submit/$',
        view  = SubmitGame.as_view(),
        name  = 'game_submit',
    ),
    url(r'^(?P<package>\S+)/$', detail_mobile, name = 'game_detail_mobile'),
)
