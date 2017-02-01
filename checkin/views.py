# -*- coding:utf-8 -*-

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from tokenapi.decorators import token_required

from tail.models import Tail
import json, random

@csrf_exempt
def check_in(request):
    if request.method == 'POST':
        import time
        today = time.strftime("%Y-%m-%d", time.localtime())

        user = request.user
        user_profile = user.get_profile()
        rspd = {}

        if user_profile.check_in_data:
            if str(user_profile.check_in_data) == today:
                    rspd['errors'] = u'今天你已签到！不能重复签到哦！'
                    rspd['msg'] = u'今天你已签到！不能重复签到哦！'
                    rspd['state'] = 3
                    rspd['success'] = False
                    res = json.dumps(rspd)
                    return HttpResponse(res)

            from datetime import datetime, timedelta
            t = (datetime.strptime(str(user_profile.check_in_data), "%Y-%m-%d") + timedelta(days = 1)).strftime('%Y-%m-%d')
            if t == today:
                user_profile.check_in += 1
            else:
                user_profile.check_in = 1
        else:
            user_profile.check_in = 1

        check_in_times = user_profile.check_in
        if check_in_times < 3:
            check_in_pp = 2
        elif 3 <= check_in_times < 7:
            check_in_pp = 5
        elif 7 <= check_in_times < 30:
            check_in_pp = 10
        elif 30 <= check_in_times:
            if check_in_times % 100 == 0:
                check_in_pp = 200
            else:
                if 30 <= check_in_times < 108:
                    check_in_pp = 20
                elif 108 <= check_in_times < 365:
                    check_in_pp = 30
                elif 365 <= check_in_times:
                    check_in_pp = 50

        tail = random.choice(Tail.objects.select_related().exclude(user=user))
        tail_string = u'@%s 对你说：“%s”'%(tail.user.username, tail.content)

        if user_profile.check_in > 3 and today == '2017-01-27' and check_in_pp < 200:
            s = random.choice([u'五仁月饼', u'豆腐脑月饼', u'咸菜肉末月饼', u'崂山月饼', u'莲蓉月饼', u'榴莲月饼', u'豆汁月饼', u'菊花瓣月饼', u'双黄月饼', u'冰皮月饼', u'豆沙月饼', u'芙蓉月饼', u'妹汁月饼'])
            check_in_pp = random.randint(100, 200)
            check_in_pp = user_profile.check_in_total
            rspd['msg'] = u"新春快乐，感谢您支持了扑家%d天，奖励%dPP以示感谢，别忘记下午2点领福包哦。"%(user_profile.check_in_total, check_in_pp)
        else:
            rspd['msg'] = u"签到成功，获得%sPP。\n%s" %(check_in_pp, tail_string)
            if check_in_times < 30 < user_profile.check_in_total:
                if random.randint(1, 100) == 1:
                    t = 29 - check_in_times
                    user_profile.check_in += t
                    rspd['msg'] = u'签到成功，获得%sPP，天降鸿福，连续签到数增加%d天！。\n%s'%(check_in_pp, t, tail_string)
        user_profile.pp += check_in_pp
        user_profile.check_in_data = today
        user_profile.check_in_total += 1
        user_profile.save()
        rspd['state'] = 1
        rspd['success'] = True
        rspd['user_pp'] = user_profile.pp
        rspd['user_check_in'] = user_profile.check_in
        rspd['user_check_in_total'] = user_profile.check_in_total
        res = json.dumps(rspd)
        return HttpResponse(res)
    else:
        return HttpResponse('Only POST is allowed')
