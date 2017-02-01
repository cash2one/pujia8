from django.template import Library
from django.contrib.auth.models import User
from django.core.cache import cache

from pujia_comments.models import PujiaComment

register = Library()

@register.inclusion_tag('lbforum/tags/dummy.html')
def show_hot_comments(template='pujia_comments/widgets/show_hot_comments_widget.html'):
    hot_comments = PujiaComment.objects.select_related().filter(hot = True, target__contains = 'library').order_by('-date')[:6]
    # t = []
    # k = []
    # hot_comments = []
    # for c in tmp:
    #     n = k.count(c.target)
    #     if n == 1:
    #         hot_comments.append(c)
    #     k.append(c.target)
    #     if c.target not in t:
    #         t.append(c.target)
    #         hot_comments.append(c)
    return {'template': template, 'comments': hot_comments}
