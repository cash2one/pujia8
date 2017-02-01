# -*- coding:utf-8 -*-

from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import Tail
import json, random

@login_required
def add_tail(request):
    rspd = {}
    if request.method=="POST":
        client_response = request.POST['client_response']
        if Tail.objects.select_related().filter(content=client_response).exists():
            rspd['msg'] = u'请勿重复提交。'
            res = json.dumps(rspd)
            return HttpResponse(res)
        user = request.user
        user_profile = user.get_profile()
        if user_profile.pp < 10:
            rspd['msg'] = u'保存失败，你的PP不足10。'
            res = json.dumps(rspd)
            return HttpResponse(res)
        user_profile.pp -= 10
        user_profile.save()

        t = Tail(user=user, content=client_response)
        t.save()

        rspd['msg'] = u'保存成功'
        res = json.dumps(rspd)
        return HttpResponse(res)
