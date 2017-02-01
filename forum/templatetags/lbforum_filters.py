#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import datetime

from django import template
from django.template.defaultfilters import timesince as _timesince
from django.template.defaultfilters import date as _date
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.utils.tzinfo import LocalTimezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import User
import re
import pujia_toolkit

register = template.Library()

@register.filter
def form_all_error(form):
    errors = []
    global_error = form.errors.get('__all__', '')
    if global_error:
        global_error = global_error.as_text()
    for name, field in form.fields.items():
        e = form.errors.get(name, '')
        if e:
            errors.append((field.label, force_unicode(e), ))
    return mark_safe(u'<ul class="errorlist">%s %s</ul>'
            % (global_error, ''.join([u'<li>%s%s</li>' % (k, v) for k, v in errors])))

@register.filter
def topic_state(topic):
    c = []
    if topic.closed:
        c.append('closed')
    elif topic.sticky:
        c.append('sticky')
    else:
        c.append('normal')
    return ' '.join(c)

@register.filter
def post_style(forloop):
    styles = ''
    if forloop['first']:
        styles = 'firstpost topicpost'
    else:
        styles = 'replypost'
    if forloop['last']:
        styles += ' lastpost'
    return styles

@register.filter
def online(user):
    try:
        if user.online.online():
            return _('Online')
    except:
        pass
    return _('Offline')

@register.filter
def lbtimesince(d, now=None):
    # Convert datetime.date to datetime.datetime for comparison.
    if not d:
        return ''
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime.datetime):
        now = datetime.datetime(now.year, now.month, now.day)
    if not now:
        if d.tzinfo:
            now = datetime.datetime.now(LocalTimezone(d))
        else:
            now = datetime.datetime.now()
    # ignore microsecond part of 'd' since we removed it from 'now'
    delta = now - (d - datetime.timedelta(0, 0, d.microsecond))
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since // (60 * 60 * 24) < 30:
        return _("%s ago") % _timesince(d)
    return _date(d, "Y-m-d H:i")

@register.filter
def pujia_text(text):
    return pujia_toolkit.pujia_text(text)

@register.filter
def Countdown(publish_time):
    import datetime
    d1 = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
    d2 = datetime.datetime.strptime(publish_time.strftime("%Y-%m-%d"), "%Y-%m-%d")
    days = (d2 - d1).days
    if days == 0:
        return '今天发布'
    else:
        return '%d 天'%days

@register.filter
def wish_rate(wish):
    return wish.pp_now * 100 / wish.pp_need
