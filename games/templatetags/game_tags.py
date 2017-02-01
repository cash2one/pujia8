#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from django import template
from forum.models import Post
from games.models import Games
from pujia_toolkit import *
from gravatar.templatetags.gravatar import gravatar_for_user

register = template.Library()

@register.simple_tag
def game_topic(topic_id):
    try:
        post = Post.objects.select_related().get(topic__id = topic_id, topic_post = True)
    except:
        return '找不到此ID，请填写正确的ID。如帖子/topic/9521/，ID为9521。'

    user = post.posted_by
    user_profile = user.get_profile()
    if user_profile.avatar:
        avatar_url = user_profile.avatar.url
    else:
        avatar_url = '/static/img/tx.jpg'
    user_info = u'''<div class="alert alert-info">
	<table>
	    <tbody>
	    <tr>
	        <td width="68" valign="top" style="text-align: center">
	            <img src="%s" alt="%s" width="68" height="68">
	        </td>
	        <td width="10"></td>
	        <td width="auto" valign="top">
	        	<p>本文作者：<a target="_blank" href="/user/%s/">%s</a><br>
	        	原帖链接：<a target="_blank" href="/topic/%s/">http://www.pujia8.com/topic/%s/</a><br>
	        	尊重原作者，转载请注明本信息！</p>
	        </td>
	    </tr>
	    </tbody>
	</table>
</div>'''%(avatar_url, user.username, user.id, user.username, topic_id, topic_id)
    return user_info + pujia_text(post.message)

@register.simple_tag
def team_info(game_id):
    game = Games.objects.select_related().get(id = game_id)
    if game.team:
        if u'扑家' in game.team and u'联运' not in game.team:
            p = '''<div><div class="alert alert-info"><p>
            <i class="icon-info-sign"></i> 扑家汉化组长期招募：<a target="_blank" href="/articles/164/">http://www.pujia8.com/articles/164/</a><br>
            <i class="icon-info-sign"></i> 扑家评测/攻略组招募：<a target="_blank" href="/topic/5726/">http://www.pujia8.com/topic/5726/</a><br>
            <i class="icon-info-sign"></i> 最新汉化资讯可关注我们的微博：<a target="_blank" href="http://weibo.com/pujiahh">http://weibo.com/pujiahh</a><br>
            <i class="icon-info-sign"></i> 此汉化为本组原创汉化，未经许可严禁盗用汉化文本。</p>
            </div></div>'''
        else:
            p = ''
        for platform in game.platform.all():
            if platform.platform == 'Android' or platform.platform == 'iOS':
                p += '<p class="alert alert-success">扑家手游交流群：152154195 欢迎加入讨论、领取礼包等</p>'
                break
        return p
    else:
        return ''

@register.simple_tag
def language_label(game_language):
    if game_language == 'cn':
        label = '<span class="label label-info">中</span>'
    elif game_language == 'jp':
        label = '<span class="label label-inverse">日</span>'
    elif game_language == 'en':
        label = '<span class="label">英</span>'
    else:
        label = ''
    return label

@register.simple_tag
def attr_label(game):
    if 'Android' not in [pf.platform for pf in game.platform.all()]:
        return ''
    html = u''
    if game.network:
        html += u'<code>需联网</code> '
    if game.vpn:
        html += u'<code>需VPN</code> '
    if game.Advertisement:
        html += u'<code>有广告</code> '
    if game.google_framework:
        html += u'<code>需谷歌框架</code> '
    if game.iap:
        html += u'<code>有内购</code> '
    if html:
        return u'游戏属性：' + html
    else:
        return ''

@register.simple_tag
def qiuhanhua_num(game):
    num = game.qiuhanhua.all().count()
    return num

@register.simple_tag
def download_link(game):
    if 'http' in game.apk_name:
        apk_link = game.apk_name
    else:
        apk_link = 'https://d.pujia8.com/apk/%s'%(game.apk_name)
    return apk_link

@register.simple_tag
def wdj_link(game):
    return 'http://www.wandoujia.com/apps/%s'%(game.apk_name_wdj[:-4].split('/')[-1])

from games.models import GameScore
@register.simple_tag
def game_score(game_id):
    scores = GameScore.objects.select_related().filter(game__id = game_id).order_by('id')
    msg = ''
    if scores:
        msg = u'<div id="scores_list"><span class="score-num">%sP</span>'%scores.count()
        for i, score in enumerate(scores):
            user = score.user
            user_profile = user.get_profile()
            msg += '<div class="score-img" title="第%d位 %s %sPP">%s</div>'%(i+1, user.username, score.pp, gravatar_for_user(user, size=36))
        msg += '</div>'
    return msg

class GetGamesListNode(template.Node):
    """
    Comments list tempalte tag class
    """
    def __init__(self, object, varname):
        """
        The class constructor
        """
        self.object  = template.Variable(object)
        self.varname = varname

    def render(self, context):
        """
        Push comments list into template context
        """
        object = self.object.resolve(context)
        gid_list = [int(i) for i in object.split(',')]

        queryset = Games.objects.select_related().filter(id__in = gid_list)
        context[self.varname] = queryset
        return ''

def _update_context(parser, token, cls):
    """
    Helper for generation update template context tags.

    First and second argument is `parser` and `token` corresponds with
    input argument for any template tag. Third argument `cls` is Node
    subclass that changes template context

    {% TAGNAME for `object` as `varname` %}
    """
    bits = token.split_contents()

    if len(bits) != 5:
        raise template.TemplateSyntaxError, '%s: wrong number or args' % bits[0]

    if bits[1] != 'for':
        raise template.TemplateSyntaxError, '%s: first word must ' % bits[0]+ \
                                            'be `for`'
    if bits[3] != 'as':
        raise template.TemplateSyntaxError, '%s: third word must ' % bits[0]+ \
                                            'be `as`'
    return cls(bits[2], bits[4])


def get_games_list(parser, token):
    """
    {% get_games_list for `object` as `varname` %}
    """
    return _update_context(parser, token, GetGamesListNode)

register.tag(get_games_list)
