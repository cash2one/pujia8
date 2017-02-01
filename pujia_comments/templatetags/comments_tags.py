# -*- coding: utf-8 -*-

from django import template
from pujia_comments.models import PujiaComment, CommentPositive
from pujia_comments.forms import CommentsOrderForm
from games.models import Games
from easy_thumbnails.files import get_thumbnailer

options = {'size': (100, 100), 'quality': 85}
register = template.Library()

class CommentNodeBase(template.Node):
    """
    Base comment node class
    """

class GetCommentsListNode(CommentNodeBase):
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
        request = context['request']
        object = self.object.resolve(context)

        ob = request.GET.get('comments_order_by')
        orderform = CommentsOrderForm(request.GET)
        if not ob:
            if 'comments_order_by' in request.COOKIES:
                ob = request.COOKIES["comments_order_by"]
            else:
                ob = '-date'
            orderform = CommentsOrderForm(request.COOKIES)

        queryset = PujiaComment.objects.select_related().filter(target = request.path).order_by(ob)
        context[self.varname] = queryset
        context['orderform'] = orderform
        return ''

class GetHotCommentsListNode(CommentNodeBase):
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
        request = context['request']
        object = self.object.resolve(context)

        ob = request.GET.get('comments_order_by')
        orderform = CommentsOrderForm(request.GET)
        if not ob:
            if 'comments_order_by' in request.COOKIES:
                ob = request.COOKIES["comments_order_by"]
            else:
                ob = '-date'
            orderform = CommentsOrderForm(request.COOKIES)

        queryset = PujiaComment.objects.select_related().filter(target = request.path, hot = True).order_by(ob)
        context[self.varname] = queryset
        context['orderform'] = orderform
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


def get_comments_list(parser, token):
    """
    {% get_comments_list for `object` as `varname` %}
    """
    return _update_context(parser, token, GetCommentsListNode)


def get_hot_comments_list(parser, token):
    """
    {% get_hot_comments_list for `object` as `varname` %}
    """
    return _update_context(parser, token, GetHotCommentsListNode)


register.tag(get_comments_list)
register.tag(get_hot_comments_list)


@register.inclusion_tag('lbforum/tags/dummy.html', takes_context = True)
def render_comments_form(context, template='pujia_comments/pujia_comments_form.html'):
    request = context['request']
    user = request.user
    target = request.path
    return {'template': template, 'user': user, 'request': request}


@register.simple_tag
def comments_count(path):
    num = PujiaComment.objects.select_related().filter(target = path).count()
    return num


@register.simple_tag
def get_comment_target(comment):
    target = comment.target
    if 'library' in target:
        gid = int(target.split('/')[2])
        try:
            game = Games.objects.select_related().get(id = gid)
            return '评论于<a target="_blank" title="%s中文汉化版发布" href="/library/%s/#comments">【%s】</a>'%(game.title_cn, game.id, game.title_cn)
        except:
            return ''
    else:
        return '<a target="_blank" title="%s" href="%s#comments">查看来源</a>'%(comment.content, target)

@register.simple_tag
def get_comment_game_img(comment):
    target = comment.target
    if 'library' in target:
        gid = int(target.split('/')[2])
        game = Games.objects.select_related().get(id = gid)
        return '<img height="100px" src="%s" alt="%s">'%(get_thumbnailer(game.imagefile).get_thumbnail(options).url, game.title_cn)
    else:
        return '<a target="_blank" title="%s" href="%s#comments">查看来源</a>'%(comment.content, target)

@register.simple_tag
def get_comment_game_title(comment):
    target = comment.target
    if 'library' in target:
        gid = int(target.split('/')[2])
        game = Games.objects.select_related().get(id = gid)
        return '<a target="_blank" title="%s中文汉化版发布" href="/library/%s/#comments"><strong>%s</strong></a>'%(game.title_cn, game.id, game.title_cn)
    else:
        return '<a target="_blank" title="%s" href="%s#comments">查看来源</a>'%(comment.content, target)

@register.simple_tag
def hot_comments_count(path):
    num = PujiaComment.objects.select_related().filter(target = path, hot = True).count()
    return num

@register.simple_tag(takes_context = True)
def get_like_link(context, comment):
    request = context['request']
    if not request.user.is_authenticated():
        return u'赞TA(%s)'%(comment.positive)
    elif request.user == comment.name:
        return u'赞TA(%s)'%(comment.positive)
    elif CommentPositive.objects.select_related().filter(user=request.user, comment=comment).exists():
        return u'赞TA(%s)'%(comment.positive)
    else:
        return u'<a title="如果你喜欢此条评论，请给TA点赞，点赞不会扣PP" href="/comment/like/%s/">赞TA(%s)</a>'%(comment.id, comment.positive)
