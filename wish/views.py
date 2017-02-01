# -*- coding:utf-8 -*-

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import Wish, WishRecord
import json

def wish_detail(request, wid):
    wish = Wish.objects.select_related().get(pk = wid)
    return HttpResponseRedirect('/wish/%s/'%wish.slug)

def wish_detail_slug(request, slug):
    wish = Wish.objects.select_related().get(slug = slug)
    wid = wish.id
    if request.method == 'POST':
        rspd = {}
        user = request.user
        if not user.is_authenticated():
            rspd['msg'] = u'你尚未登录，请先登录。'
            res = json.dumps(rspd)
            return HttpResponse(res)
        user_profile = user.get_profile()
        client_response = request.POST['client_response']
        if not client_response:
            rspd['msg'] = u'请先输入PP值'
            res = json.dumps(rspd)
            return HttpResponse(res)
        wish_value = int(client_response)
        if wish_value < 100:
            rspd['msg'] = u'每次至少需投100PP。'
            res = json.dumps(rspd)
            return HttpResponse(res)
        if user_profile.pp < wish_value:
            rspd['msg'] = u'你的PP不足！'
            res = json.dumps(rspd)
            return HttpResponse(res)
        user_profile.pp -= wish_value
        user_profile.save()
        wish.pp_now += wish_value
        wish.save()
        try:
            wr = WishRecord.objects.select_related().get(tar_wish__id = wid, user = user)
            wr.pp_wish += wish_value
            wr.save()
        except WishRecord.DoesNotExist:
            wr = WishRecord(tar_wish = wish, user = user, pp_wish = wish_value)
            wr.save()
        rspd['msg'] = u'感谢你的许愿！'
        res = json.dumps(rspd)
        return HttpResponse(res)
    else:
        rate = wish.pp_now * 100 / wish.pp_need
        wrs = WishRecord.objects.select_related().filter(tar_wish__id = wid).order_by('-pp_wish', 'id')
        return render_to_response('wish/wish_detail.html', {'wish': wish, 'rate': rate, 'wrs': wrs},
            context_instance=RequestContext(request))
