# -*- coding:utf-8 -*-

from django.http import HttpResponseRedirect
from models import Link
import time

def Redirect(request, lid):
    url = Link.objects.select_related().get(pk = lid)
    month = time.strftime("%m", time.localtime())

    fn = 'link/logs/%s_mon_%s.csv'%(url.slug, month)
    try:
        dat = open(fn, 'rb').read()
    except:
        dat = ''
    ip = request.META['REMOTE_ADDR']
    if ip not in dat:
        url.count += 1
        url.todaycount += 1
        url.monthcount += 1
        url.save()

        dst = open(fn, 'ab+')
        add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        dst.write('%s, %s\r\n'%(ip, add_time))
        dst.close()
    return HttpResponseRedirect(url.url)
