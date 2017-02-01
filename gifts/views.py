# -*- coding:utf-8 -*-

from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
import json, random
from models import Gifts, Cdkeys_Table, Cdkeys_Record

def list(request):
    gifts = Gifts.objects.select_related().filter(post=True).order_by('-add_time')
    return render(request, 'gifts/list.html',{'gifts': gifts})

def exchange(request, gift_id):
    rspd = {}
    user = request.user
    user_profile = user.get_profile()
    gift = Gifts.objects.select_related().get(pk = gift_id)
    if gift.cdkeys.all().count() == 0:
        msg = u'此礼包已被领光。'
    elif user_profile.check_in < gift.days and user_profile.check_in_total < 30:
        msg = u'需连签数大于%d天或者总签数大于30天，才能抽此礼包。'%gift.days
    elif user_profile.pp < gift.pp:
        msg = u'你的PP不足。'
    elif Cdkeys_Record.objects.select_related().filter(gifts=gift, user=user).exists():
        msg = u'你已经拿过此礼包了。'
    elif random.randint(1, 10000) <= int(gift.rate):
        cdkeys = gift.cdkeys.all()
        cdkey = random.choice(cdkeys)
        key = cdkey.cdkey
        msg = u'恭喜，兑换码为%s，快去使用吧。'%key

        if key[:2] == 'pp':
            user_profile.pp += int(key[2:])

        user_profile.pp -= gift.pp
        user_profile.save()

        cr = Cdkeys_Record(gifts=gift, user=user, cdkey=cdkey.cdkey)
        cr.save()
        cdkey.delete()

        gift.times += 1
        gift.save(update_fields = ['times'])
    else:
        user_profile.pp -= gift.pp
        user_profile.save(update_fields = ['pp'])
        msg = u'很遗憾未抽中。'
        gift.times += 1
        gift.save(update_fields = ['times'])
    rspd['msg'] = msg
    res = json.dumps(rspd)
    return HttpResponse(res)
