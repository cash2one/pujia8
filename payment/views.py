# -*- coding:utf-8 -*-

from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from alipay.alipay import *
import time

@login_required
def payment(request, value):
    user = request.user
    tn = '%s_%d_%s'%(time.time(), user.id, value)
    subject = u'扑家吧充值: ' + str(int(value) * 20) + 'PP'
    url=create_direct_pay_by_user (tn, subject, u'扑家吧充值', value)
    return HttpResponseRedirect (url)

@login_required
def return_url_handler(request):
    if notify_verify(request.GET):
        tn = request.GET.get('out_trade_no')
        value = int(tn.split('_')[-1])
        uid = int(tn.split('_')[1])
        user = User.objects.select_related().get(id = uid)
        u = user.get_profile()
        u.pp += value * 20
        u.save()
        return HttpResponseRedirect (reverse ('payment_success'))
    return HttpResponseRedirect (reverse ('payment_error'))

@csrf_exempt
def notify_url_handler(request):
    if request.method == 'POST':
        if notify_verify(request.POST):
            tn = request.POST.get('out_trade_no')
            trade_status = request.POST.get('trade_status')
            trade_no=request.POST.get('trade_no')
            value = int(tn.split('_')[-1])
            uid = int(tn.split('_')[1])
            user = User.objects.select_related().get(id = uid)
            u = user.get_profile()
            u.pp += value * 20
            u.save()
            return HttpResponse ("success")
        return HttpResponse ("fail")
