#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from django import template
from flow.models import *
from easy_thumbnails.files import get_thumbnailer
from tagging.models import Tag, TaggedItem
import re

register = template.Library()
options = {'size': (280, 160), 'quality': 85, 'crop': 'smart'}

@register.simple_tag
def show_img(flow):
    video_info = Video_info.objects.select_related().filter(flow = flow)
    if video_info.exists():
        img_url = video_info[0].cover
    elif flow.head_img:
        img_url = flow.head_img[8:]
    else:
        img_url = 'pics/20161019140858_100.jpg'
    try:
        html = '<img width="280px" height="160px" src="%s" alt="pp">' % get_thumbnailer(img_url).get_thumbnail(options).url
    except:
        html = '<img width="280px" height="160px" src="%s" alt="pp">' % get_thumbnailer('pics/20161019140858_100.jpg').get_thumbnail(options).url
    return html

@register.simple_tag
def play_video(flow):
    if 'bilibili' in flow.url:
        _re_bili = re.compile('http://www.bilibili.(tv|com)/video/av([A-Za-z0-9]+)/', re.UNICODE|re.I|re.M|re.S)
        html = _re_bili.sub(r'<embed src="https://static-s.bilibili.com/miniloader.swf?aid=\2&page=1" allowscriptaccess="never" allowFullScreen="true" quality="high" flashvars="playMovie=true&auto=1" width="600" height="480" align="middle"  type="application/x-shockwave-flash" wmode="transparent"></embed>', flow.url)
        return '<p>%s</p>'%html
    else:
        return ''

@register.inclusion_tag('flow/widgets/index_news.html', takes_context=True)
def index_news(context):
    flows = Flow.objects.select_related().filter(hot = True, post = True).order_by('-add_time')[:8]
    column = Column.objects.select_related().filter(display = True).order_by('-order')
    context['flows'] = flows
    context['columns'] = column
    return context

@register.inclusion_tag('flow/widgets/news_crumbs.html', takes_context=True)
def column_news(context, column):
    flows = Flow.objects.select_related().filter(column = column, post = True).order_by('-add_time')[:8]
    context['flows'] = flows
    return context

@register.inclusion_tag('flow/widgets/news_related.html', takes_context=True)
def related_news(context, flow):
    flows = TaggedItem.objects.get_union_by_model(Flow, flow.tags.split(' ')).distinct().filter(post = True).exclude(id=flow.pk).order_by(
        '-add_time')[:6]
    context['flows'] = flows
    return context
