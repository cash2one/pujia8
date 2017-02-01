# -*- coding:utf-8 -*-

from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from models import Gallery
from forms import GalleryOrderByForm
from django.contrib.auth.models import User
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
import json

def index(request):
    if request.method == 'POST':
        rspd = {}
        user = request.user
        if not user.is_authenticated():
            rspd['msg'] = u'你尚未登录，请先登录。'
            res = json.dumps(rspd)
            return HttpResponse(res)
        url = request.POST['client_response']
        user_profile = user.get_profile()
        if user_profile.pp < 100:
            rspd['msg'] = u'保存失败，你的PP不足100。'
            res = json.dumps(rspd)
            return HttpResponse(res)

        gallery = Gallery.objects.select_related().get(imagefile = url)
        gallery.count += 1
        gallery.save()
        gallery_user_profile = gallery.user.get_profile()
        gallery_user_profile.pp += 10
        gallery_user_profile.save()

        user_profile.background = url
        user_profile.pp -= 100
        user_profile.save()

        rspd['msg'] = u'保存成功'
        res = json.dumps(rspd)
        return HttpResponse(res)
    else:
        ob = request.GET.get('gallery_order_by')
        orderform = GalleryOrderByForm(request.GET)
        if not ob:
            if 'gallery_order_by' in request.COOKIES:
                ob = request.COOKIES["gallery_order_by"]
            else:
                ob = '-add_time'
            orderform = GalleryOrderByForm(request.COOKIES)
        gallerys = Gallery.objects.select_related().all().order_by(ob, '-id')
        return render(request, 'gallery/gallery_index.html',{'gallerys': gallerys, 'orderform': orderform})
