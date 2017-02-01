#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from django import template
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from bbcode import _postmarkup
from gravatar.templatetags.gravatar import gravatar_for_user
from djangohelper.decorators import basictag
from pujia_comments.models import PujiaComment
from django.core.cache import cache
from games.models import Games
from tagging.models import Tag, TaggedItem

register = template.Library()

@register.tag
@basictag(takes_context=True)
def bbcode(context, s, has_replied=False):
    if not s:
        return ""
    tag_data = {'has_replied': has_replied}
    html = _postmarkup(s, #cosmetic_replace=False,
            tag_data=tag_data,
            auto_urls=getattr(settings, 'BBCODE_AUTO_URLS', True))
    context['hide_attachs'] = tag_data.get('hide_attachs', [])
    return html

@register.simple_tag
def forum_url(forum, topic_type, topic_type2):
    args = [forum.slug, topic_type, topic_type2]
    args = [e for e in args if e]
    return reverse('lbforum_forum', args=args)

@register.simple_tag
def page_range_info(page_obj):
    paginator = page_obj.paginator
    return paginator.count

@register.simple_tag
def page_item_idx(page_obj, forloop):
    return page_obj.start_index() + forloop['counter0']

@register.simple_tag
def page_info(num_replies):
    return (num_replies - 2)/15 + 1

@register.simple_tag
def user_label(user):
    label = cache.get('user_label_uid%s'%user.id)
    if not label:
        label = ''
        user_profile = user.get_profile()
        if user_profile.verify:
            label += '''<a href="#" rel="popover" data-content="%s" data-original-title="%s"><i class="icon-verify"></i></a>'''%(user_profile.verify, user.username)
        if user_profile.state == '2':
            label += '''<i title="版主" class="icon-banzhu"></i>'''
        if user_profile.female:
            label += '''<i title="I'm a 妹纸，私に親切にしてください！" class="icon-female"></i>'''
        if user_profile.super_comment > 0:
            label += ''' <small>%d弹</small>'''%user_profile.super_comment
        if user_profile.gp > 0:
            label += ''' <small>%dGP</small>''' % user_profile.gp
        cache.set('user_label_uid%s'%user.id, label, 3600)
    return label

@register.simple_tag
def xianliaome(user):
    import time, hashlib
    js = ''
    ptime = time.time()
    uid = 0
    name = ''
    avatar = ''
    if user.is_authenticated():
        uid = user.id
        name = user.username
        if user.get_profile().avatar:
            avatar = 'http://www.pujia8.com' + user.get_profile().avatar.url
        else:
            avatar = 'http://www.pujia8.com/static/img/tx.jpg'
    hash_new = hashlib.sha512()
    hash_new.update('10091_%d_%s_FFfC9qoJtiB4QneitcfLbguPtCAe277o'%(uid, ptime))
    hash = hash_new.hexdigest()
    js = '''
    <script>
        var xlm_wid='10091';
        var xlm_url='http://www.xianliao.me/';
        var xlm_uid='%d';
        var xlm_name='%s';
        var xlm_avatar='%s';
        var xlm_time='%s';
        var xlm_hash='%s';
    </script>
    <script type='text/javascript' charset='UTF-8' src='http://www.xianliao.me/embed.js'></script>
    '''%(uid, name, avatar, ptime, hash)
    return js

@register.simple_tag
def max_score(user):
    user_profile = user.get_profile()
    min_score_pp = -1
    check_in_total = user_profile.check_in_total
    if check_in_total < 7:
        max_score_pp = 0
    if 7 <= check_in_total < 14:
        max_score_pp = 1
    if 14 <= check_in_total < 100:
        max_score_pp = 3
    if 100 <= check_in_total < 365:
        min_score_pp = -2
        max_score_pp = 6
    if 365 <= check_in_total:
        min_score_pp = -3
        max_score_pp = 9

    if user.has_perm('forum.delete_post'):
        max_score_pp = 250
        min_score_pp = -250

    if user.is_superuser:
        max_score_pp = 9999
        min_score_pp = -9999

    return "范围：%s至+%s"%(min_score_pp, max_score_pp)

from forum.models import Score
@register.simple_tag
def post_score(post_id):
    scores = Score.objects.select_related().filter(post__id = post_id).order_by('id')
    msg = ''
    if scores:
        msg = u'<div id="scores_list"><span class="score-num">%sP</span>'%scores.count()
        for i, score in enumerate(scores):
            user = score.score_by
            msg += '<div class="score-img" title="第%d位 %s %sPP">%s</div>'%(i+1, user.username, score.pp, gravatar_for_user(user, size=36))
        msg += '</div>'
    return msg

DEFAULT_PAGINATION = getattr(settings, 'PAGINATION_DEFAULT_PAGINATION', 20)
DEFAULT_WINDOW = getattr(settings, 'PAGINATION_DEFAULT_WINDOW', 4)

@register.inclusion_tag('lbforum/post_paginate.html', takes_context=True)
def post_paginate(context, count, paginate_by=DEFAULT_PAGINATION, window=DEFAULT_WINDOW):
    if not isinstance(paginate_by, int):
        paginate_by = template.Variable(paginate_by)
    if not isinstance(window, int):
        window = template.Variable(paginate_by)
    page_count = count / paginate_by
    if count % paginate_by > 0:
        page_count += 1
    context['page_count'] = page_count
    pages = []
    if page_count == 1:
        pass
    elif window >= page_count:
        pages = [e + 1 for e in range(page_count)]
    else:
        pages = [e + 1 for e in range(window-1)]
    context['pages'] = pages
    context['window'] = window
    return context

@register.inclusion_tag('lbforum/widgets/related_games.html', takes_context=True)
def related_games(context, game_id):
    related_games = cache.get('related_games_%s'%game_id)
    if not related_games:
        game = Games.objects.select_related().get(pk = game_id)
        related_games = TaggedItem.objects.get_union_by_model(Games, game.tags.split(' ')).distinct().filter(post = '1').exclude(id = game_id).order_by('-publish_time')[:5]
        cache.set('related_games_%s'%game_id, related_games, 1800)
    context['related_games'] = related_games
    return context
