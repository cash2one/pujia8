# -*- coding:utf-8 -*-

from django.shortcuts import render_to_response, render, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from models import Puji, Pay_PP
from forms import ServerForm
import time, hashlib, random, string, urllib2, json, urllib, base64

def random_str(randomlength=32):
    a = list(string.ascii_letters)
    random.shuffle(a)
    return ''.join(a[:randomlength])

def xsqst(request):
    serverid = request.GET.get('serverid')
    serverform = ServerForm(request.GET)
    if not serverid:
        if 'serverid' in request.COOKIES:
            serverid = request.COOKIES["serverid"]
        else:
            serverid = '0'
        serverform = ServerForm(request.COOKIES)
    user = request.user
    args = ''
    if user.is_authenticated():
        uid = user.email
        ptime = time.time()
        s = 'uid=%s&serverid=0&ptime=%s&isadult=1&65b8fe83281f2c28e87b426d2cea7d12'%(uid, ptime)
        sign = hashlib.md5(s.encode('utf-8')).hexdigest()
        args = 'uid=%s&serverid=0&ptime=%s&isadult=1&sign=%s'%(uid, ptime, sign)
    return render_to_response('webgames/xsqst.html', {'args': args, 'serverform': serverform}, context_instance=RequestContext(request))

def sdgundam(request):
    serverid = request.GET.get('serverid')
    serverform = ServerForm(request.GET)
    if not serverid:
        if 'serverid' in request.COOKIES:
            serverid = request.COOKIES["serverid"]
        else:
            serverid = '0'
        serverform = ServerForm(request.COOKIES)
    user = request.user
    args = ''
    if user.is_authenticated():
        uid = user.id
        ptime = time.time()
        s = 'uid=pujia8_%s&serverid=0&ptime=%s&isadult=1&63311cb5289ca5e7d30050bfcb445828'%(uid, ptime)
        sign = hashlib.md5(s.encode('utf-8')).hexdigest()
        args = 'uid=pujia8_%s&serverid=0&ptime=%s&isadult=1&sign=%s'%(uid, ptime, sign)
    return render_to_response('webgames/sdgundam.html', {'args': args, 'serverform': serverform}, context_instance=RequestContext(request))


import random, string
def random_str(randomlength=16):
    a = list(string.ascii_letters)
    random.shuffle(a)
    return ''.join(a[:randomlength])

def bspt(request):
    f = request.GET.get('f', '')
    server_id = '1'
    user = request.user
    if user.is_authenticated():
        uid = str(user.id)
    elif f == 'pjgame':
        uid = request.session.get('uid', default = '')
        if not uid:
            uid = random_str()
            request.session['uid'] = uid
    else:
        uid = ''
    ptime = time.time()
    c = 'pujia8_%s_mfasofdsifuewfjasfjaefi'%uid
    openid = 'pujia8_%s_'%uid + hashlib.md5(c.encode('utf-8')).hexdigest()
    s = '%spujiaba%s%ssaJ6GacnJfq5OVsSZjblS555uuMU2iKV'%(openid, server_id, ptime)
    sign = hashlib.md5(s.encode('utf-8')).hexdigest()
    args = 'openid=%s&pid=pujiaba&server_id=%s&time=%s&sign=%s'%(openid, server_id, ptime, sign)
    return render_to_response('webgames/bspt.html', {'args': args, 'uid': uid}, context_instance=RequestContext(request))

def czdtx(request):
    user = request.user
    param = {}
    key = ''
    ly = ''
    if user.is_authenticated():
        ly = 'pujia8'
        param['ly'] = ly
        account = "pujia8_%d"%user.id
        param['account'] = account
        zoneid = 1
        param['zoneid'] = zoneid
        ptime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        param['ptime'] = ptime
        isadult = 1
        param['isadult'] = isadult
        LOGIN_KEY = 'pujia8f6a061ff10314537a904c49cda805a28'
        s = '%s%s%d%d%s%s'%(ly, account, zoneid, isadult, ptime, LOGIN_KEY)
        sign = hashlib.md5(s.encode('utf-8')).hexdigest()
        param['sign'] = sign
        key = base64.b64encode(str(param))
    return render_to_response('webgames/czdtx.html', {'key': key, 'ly': ly}, context_instance=RequestContext(request))

def exchange_gold(request):
    if 'serverid' in request.COOKIES:
        serverid = request.COOKIES["serverid"]
    else:
        serverid = '0'
    rspd = {}
    if request.method=="POST":
        if serverid == '0':
            rspd['msg'] = u'在兑换前请先选择服务区'
            res = json.dumps(rspd)
            return HttpResponse(res)
        if request.POST['client_response'] == '':
            rspd['msg'] = u'请输入要兑换的PP值。'
            res = json.dumps(rspd)
            return HttpResponse(res)
        pp = int(request.POST['client_response'])
        user = request.user
        user_profile = user.get_profile()
        if user_profile.pp < pp:
            rspd['msg'] = u'你的PP不足。'
            res = json.dumps(rspd)
            return HttpResponse(res)
        if pp <= 0:
            rspd['msg'] = u'兑换的PP不能小于0'
            res = json.dumps(rspd)
            return HttpResponse(res)
        uid = user.email
        ptime = time.time()
        order = random_str()
        payitem = pp * 1000
        s = 'uid=%s&zoneid=%s&ptime=%s&order=%s&amount=0&payitem=%s&paydes=&debug=0&65b8fe83281f2c28e87b426d2cea7d12'%(uid, serverid, ptime, order, payitem)
        sign = hashlib.md5(s.encode('utf-8')).hexdigest()
        args = 'uid=%s&zoneid=%s&ptime=%s&order=%s&amount=0&payitem=%s&paydes=&debug=0&type=1&sign=%s'%(uid, serverid, ptime, order, payitem, sign)
        url = 'http://s1.pujia8mxwk.u77.com/pujia8/ExchangeGold.ashx?%s'%args
        response = urllib.urlopen(url).read()
        user_profile.pp -= pp
        user_profile.save()
        return HttpResponse(response)

def exchange_puji(request):
    rspd = {}
    if 'serverid' in request.COOKIES:
        serverid = request.COOKIES["serverid"]
    else:
        serverid = '0'

    if 'exchange_puji' in request.COOKIES:
        rspd['msg'] = u'请勿频繁进行兑换'
        res = json.dumps(rspd)
        return HttpResponse(res)

    if request.method=="POST":
        user = request.user
        user_profile = user.get_profile()
        if serverid == '0':
            rspd['msg'] = u'在兑换前请先选择服务区'
            res = json.dumps(rspd)
            return HttpResponse(res)
        if user_profile.pp < 1000:
            rspd['msg'] = u'你的PP不足1000，无法兑换。'
            res = json.dumps(rspd)
            return HttpResponse(res)
        if Puji.objects.select_related().filter(user = user, serverid = int(serverid)).exists():
            rspd['msg'] = u'你已经兑换过了'
            res = json.dumps(rspd)
            return HttpResponse(res)

        uid = user.email
        ptime = time.time()
        order = random_str()
        payitem = 1
        s = 'uid=%s&zoneid=%s&ptime=%s&order=%s&amount=0&payitem=%s&paydes=&debug=0&65b8fe83281f2c28e87b426d2cea7d12'%(uid, serverid, ptime, order, payitem)
        sign = hashlib.md5(s.encode('utf-8')).hexdigest()
        args = 'uid=%s&zoneid=%s&ptime=%s&order=%s&amount=0&payitem=%s&paydes=&debug=0&type=2&sign=%s'%(uid, serverid, ptime, order, payitem, sign)
        url = 'http://s1.pujia8mxwk.u77.com/pujia8/ExchangeGold.ashx?%s'%args
        response = urllib.urlopen(url).read()
        dic = json.loads(response)
        if dic['status'] == '1':
            user_profile.pp -= 1000
            user_profile.save()
            p = Puji(user = user, serverid = int(serverid))
            p.save()
        return HttpResponse(response)

def get_pay_pp(request):
    rspd = {}
    if 'serverid' in request.COOKIES:
        serverid = request.COOKIES["serverid"]
    else:
        serverid = '0'

    user = request.user
    user_profile = user.get_profile()
    if serverid == '0':
        rspd['msg'] = u'请先选择服务区'
        res = json.dumps(rspd)
        return HttpResponse(res)
    uid = user.email
    url = 'http://s1.pujia8mxwk.u77.com/pujia8/getuserinfo.ashx?uid=%s&serverid=%s'%(uid, serverid)
    response = urllib.urlopen(url).read()
    dic = json.loads(response)
    paycount = int(dic['paycount']) / 10
    if paycount == 0:
        rspd['msg'] = u'1分都不给我，还想领PP？'
        res = json.dumps(rspd)
        return HttpResponse(res)
    pay_pp = Pay_PP.objects.select_related().filter(user = user, game='xsqst', serverid = int(serverid))
    if pay_pp.exists():
        pay_pp = pay_pp[0]
        pp = paycount - pay_pp.value
        pay_pp.value = paycount
        pay_pp.save()
    else:
        pp = paycount
        p = Pay_PP(user = user, game='xsqst', serverid = int(serverid), value = paycount)
        p.save()
    user_profile.pp += pp
    user_profile.save()
    rspd['msg'] = u'成功领取%dPP'%pp
    res = json.dumps(rspd)
    return HttpResponse(res)

def yxhg(request):
    args = ''
    return render_to_response('webgames/yxhg.html', {'args': args}, context_instance=RequestContext(request))

def yxhg_play(request):
    user = request.user
    args = ''
    if user.is_authenticated():
        uid = '1020_pujia%d'%user.id
        ptime = time.time()
        ip = request.META['REMOTE_ADDR']
        s = '11020%s117%s839ba292c49ed94a1289e83762c382169'%(uid, ptime)
        sign = hashlib.md5(s.encode('utf-8')).hexdigest()
        args = 'unid=1020&uid=%s&cm=1&sid=1&gid=17&time=%s&ip=%s&sign=%s'%(uid, ptime, ip, sign)
    return render_to_response('webgames/yxhg_play.html', {'args': args}, context_instance=RequestContext(request))

def jjdjl(request):
    args = ''
    return render_to_response('webgames/jjdjl.html', {'args': args}, context_instance=RequestContext(request))

def jjdjl_play(request):
    user = request.user
    args = ''
    if user.is_authenticated():
        uid = '1020_pujia%d'%user.id
        ptime = time.time()
        ip = request.META['REMOTE_ADDR']
        s = '11020%s123%s839ba292c49ed94a1289e83762c382169'%(uid, ptime)
        sign = hashlib.md5(s.encode('utf-8')).hexdigest()
        args = 'unid=1020&uid=%s&cm=1&sid=1&gid=23&time=%s&ip=%s&sign=%s'%(uid, ptime, ip, sign)
    return render_to_response('webgames/jjdjl_play.html', {'args': args}, context_instance=RequestContext(request))
