#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from django import template
from gifts.models import Gifts, Cdkeys_Record

register = template.Library()

@register.simple_tag
def gifts_num(gift_id):
    gift = Gifts.objects.select_related().get(pk = gift_id)
    return gift.cdkeys.all().count()

@register.simple_tag
def gifts_rate(gift_id):
    gift = Gifts.objects.select_related().get(pk = gift_id)
    if gift.rate%100 == 0:
        return gift.rate/100
    else:
        return float(gift.rate)/100.0

@register.simple_tag(takes_context=True)
def exchange_btn(context, gift_id):
    gift = Gifts.objects.select_related().get(pk = gift_id)
    request = context['request']
    user = request.user
    if user.is_authenticated():
        cr = Cdkeys_Record.objects.select_related().filter(gifts=gift, user=user)
        if cr.exists():
            return '''<div class="alert alert-info">已抽：%s</div>'''%cr[0].cdkey
        else:
            return '''<button class="btn btn-primary dropdown-toggle" onclick="location.href='javascript:exchange(%s)'">我抽</button>'''%gift_id
    else:
        return '''<button class="btn btn-inverse dropdown-toggle">请先登录</button>'''
