# -*- coding:utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
import accountviews

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^', include('forum.urls')),
    (r'^request/', include('request.urls')),
    (r'^account/', include('account.urls')),
    (r'^articles/', include('articles.urls')),
    (r'^library/', include('games.urls')),
    (r'^webgames/', include('webgames.urls')),
    (r'^gifts/', include('gifts.urls')),
    (r'^wish/', include('wish.urls')),
    (r'^checkin/', include('checkin.urls')),
    (r'^weixin/', include('weixin.urls')),
    (r'^gallery/', include('gallery.urls')),
    (r'^link/', include('link.urls')),
    (r'^tail/', include('tail.urls')),
    (r'^api/', include('api.urls')),
    (r'^news/', include('flow.urls')),
    (r'^payment/', include('payment.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^redactor/', include('redactor.urls')),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^comment/', include('pujia_comments.urls')),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './static'}),
)

from django.views.decorators.cache import cache_page
from django.contrib.sitemaps import views as sitemaps_views
from django.contrib.sitemaps import GenericSitemap
from games.models import Games
from forum.models import Topic

games_info_dict = {
    'queryset': Games.objects.all(),
    'date_field': 'publish_time',
}

topics_info_dict = {
    'queryset': Topic.objects.all(),
    'date_field': 'created_on',
}

sitemaps = {
    'games': GenericSitemap(games_info_dict, priority=1.0, changefreq='daily'),
    'topics': GenericSitemap(topics_info_dict, priority=0.6),
}

urlpatterns += patterns('',
    url(r'^user/(?P<user_id>\d+)/$', login_required(accountviews.profile), name='lbforum_user_profile'),
    url(r'^sitemap\.xml$', cache_page(86400)(sitemaps_views.sitemap), {'sitemaps': sitemaps}, name='sitemaps'),
)
