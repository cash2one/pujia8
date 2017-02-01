from django.template import Library
from django.contrib.auth.models import User
from django.core.cache import cache

from forum.models import Topic, Category, Forum, Post
from games.models import Games, Collection
import datetime

register = Library()

@register.inclusion_tag('lbforum/tags/dummy.html')
def lbf_categories_and_forums(forum=None, template='lbforum/widgets/categories_and_forums.html'):
    categories = cache.get('categories')
    if not categories:
        categories = Category.objects.all()
        cache.set('categories', categories, 1800)
    return {'template': template, 'forum': forum, 'categories': categories}

@register.inclusion_tag('lbforum/tags/dummy.html')
def lbf_status(template='lbforum/widgets/lbf_status.html'):
    return {'template': template,
            'total_topics': Topic.objects.count(),
            'total_posts': Post.objects.count(),
            'total_users': User.objects.count(),
            'last_registered_user': User.objects.order_by('-date_joined')[0]}

@register.inclusion_tag('lbforum/tags/dummy.html')
def rank_topics(template='lbforum/widgets/rank_topics.html'):
    date1 = datetime.date.today()
    week_start_dt = date1-datetime.timedelta(days=7)
    week_end_dt = date1
    month_start_dt = date1-datetime.timedelta(days=30)
    month_end_dt = date1
    weekly_topics = cache.get('weekly_topics')
    if not weekly_topics:
        weekly_topics = Topic.objects.select_related().filter(created_on__gte = week_start_dt, \
                                                              created_on__lte = week_end_dt).order_by('-num_views')[:10]
        cache.set('weekly_topics', weekly_topics, 1800)
    month_topics = cache.get('month_topics')
    if not month_topics:
        month_topics = Topic.objects.select_related().filter(created_on__gte = month_start_dt, \
                                                             created_on__lte = month_end_dt).order_by('-num_views')[:10]
        cache.set('month_topics', month_topics, 1800)
    return {'template': template, 'weekly_topics': weekly_topics, 'month_topics': month_topics}

@register.inclusion_tag('lbforum/tags/dummy.html')
def rank_games(template='lbforum/widgets/rank_games.html'):
    new_games = cache.get('new_games')
    if not new_games:
        new_games = Games.objects.select_related().filter(post='1', state='1').order_by('-publish_time')[:6]
        cache.set('new_games', new_games, 1800)
    hot_games = cache.get('hot_games')
    if not hot_games:
        hot_games = Games.objects.select_related().filter(post='1', state='1', hot='1').order_by('-publish_time')[:6]
        cache.set('hot_games', hot_games, 1800)
    return {'template': template, 'new_games': new_games, 'hot_games': hot_games}

@register.inclusion_tag('lbforum/tags/dummy.html')
def lianyun_games(template='lbforum/widgets/lianyun_games.html'):
    lianyun_games = cache.get('lianyun_games')
    if not lianyun_games:
        lianyun_games = Games.objects.select_related().filter(post='1', state='1', lianyun=True).order_by('-publish_time')[:5]
        cache.set('lianyun_games', lianyun_games, 1800)
    return {'template': template, 'lianyun_games': lianyun_games}

@register.inclusion_tag('lbforum/tags/dummy.html')
def collection(template='lbforum/widgets/collection_list.html'):
    collection_list = Collection.objects.select_related().filter(post='1').order_by('-lastFetchTime')
    return {'template': template, 'collection_list': collection_list}

@register.inclusion_tag('lbforum/tags/dummy.html', takes_context = True)
def cur_user_profile(context, template='lbforum/widgets/cur_user_profile.html'):
    import time
    today = time.strftime("%Y-%m-%d", time.localtime())

    request = context['request']
    user = request.user
    cic = False
    if user.is_authenticated():
        user_profile = user.get_profile()
        if user_profile.check_in_data:
            if str(user_profile.check_in_data) == today:
                cic = True
    return {'template': template, 'cic': cic, 'user': user, 'request': request}

@register.inclusion_tag('lbforum/tags/dummy.html', takes_context = True)
def cur_user_profile_index(context, template='lbforum/widgets/cur_user_profile_index.html'):
    import time
    today = time.strftime("%Y-%m-%d", time.localtime())

    request = context['request']
    user = request.user
    cic = False
    if user.is_authenticated():
        user_profile = user.get_profile()
        if user_profile.check_in_data:
            if str(user_profile.check_in_data) == today:
                cic = True
    return {'template': template, 'cic': cic, 'user': user, 'request': request}
