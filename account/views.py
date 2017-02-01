# -*- coding:utf-8 -*-

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from forms import RegisterForm, LoginForm, ChangePasswordForm
from models import Profile
from gallery.models import Gallery
import json,os,re

import time
today = time.strftime("%Y-%m-%d", time.localtime())

def make_avatar(file_obj):
    import time, random
    fn = time.strftime('%Y%m%d%H%M%S')
    fn = fn + '_%d' %random.randint(0, 100)

    url = 'static/avatars/%s.jpg'%fn
    from PIL import Image, ImageFile
    parser = ImageFile.Parser()
    for chunk in file_obj.chunks():
        parser.feed(chunk)
    img = parser.close()
    w, h = img.size
    if w != 80 or h != 80:
        if w > h:
            diff = (w - h) / 2
            img = img.crop((diff, 0, w - diff, h))
        else:
            diff = (h - w) / 2
            img = img.crop((0, diff, w, h - diff))
        img = img.resize((80, 80), Image.ANTIALIAS)
        if img.mode != "RGB":
            img = img.convert("RGB")
    img.save(url, quality = 90)
    return url[7:]

def register(request):
    next = request.GET.get('next', '/')
    if request.method=="POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            try:
                file_obj = request.FILES['avatar']
                url = make_avatar(file_obj)
            except:
                url = ''
            next = request.POST["next"]
            if next == 'None':
                next = '/'
            user = User.objects.create_user(username,email,password)
            profile = Profile(user=user, avatar=url, today=today)
            profile.save()
            user.save()
            return HttpResponseRedirect("/account/login/?f=register&next=%s"%next)
    else:
        form = RegisterForm()
    return render_to_response("account/register.html",{'form': form, 'next': next},\
                        context_instance=RequestContext(request))

def login(request):
    next = request.GET.get('next', '/')
    f = request.GET.get('f', '')
    if request.method == 'POST':
        form = LoginForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            next = request.POST["next"]
            if next == 'None':
                next = '/'
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect('/')
    else:
        form = LoginForm()
    return render_to_response("account/login.html",{'form': form, 'next': next, 'f': f},\
                        context_instance=RequestContext(request))

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')

img_ext = ['.jpg', '.jpeg', '.gif', '.png', '.bmp']
@login_required
def change_avatar(request):
    user = request.user
    if request.method=="POST":
        file_obj = request.FILES['avatarupload']
        if file_obj.size > 2097152:
            return HttpResponse('不能上传超过2M大小的图片')

        import os
        ext = os.path.splitext(file_obj.name)[1].lower()
        if ext in img_ext:
            url = make_avatar(file_obj)
            profile = Profile.objects.select_related().get(user=user)
            profile.avatar = url
            profile.save()
            return HttpResponseRedirect('/account/change/avatar/')
        else:
            return HttpResponse('不允许上传此类型的图片')
    else:
        avatar = user.get_profile().avatar
        return render_to_response("account/change_avatar.html",{'avatar': avatar},\
                        context_instance=RequestContext(request))

@csrf_exempt
@login_required
def change_background(request):
    rspd = {}
    if request.method=="POST":
        file_obj = request.FILES['filetoupload']
        if file_obj.size > 3145728:
            rspd['status'] = 503
            rspd['msg'] = u'不能上传超过3M大小的图片'
            res = json.dumps(rspd)
            return HttpResponse(res)
        ext = os.path.splitext(file_obj.name)[1].lower()
        if ext not in img_ext:
            rspd['status'] = 503
            rspd['msg'] = u'不允许上传此格式的图片'
            res = json.dumps(rspd)
            return HttpResponse(res)
        import time, random
        fn = time.strftime('%Y%m%d%H%M%S')
        fn = fn + '_%d' %random.randint(0,100)
        url = 'static/background/%s.jpg'%fn
        from PIL import ImageFile, Image
        parser = ImageFile.Parser()
        for chunk in file_obj.chunks():
            parser.feed(chunk)
        img = parser.close()
        img.convert(mode='RGB').save(url, quality = 80)

        rspd['status'] = 200
        rspd['msg'] = u'成功上传'
        rspd['url'] = '/' + url
        res = json.dumps(rspd)
        return HttpResponse(res)

@login_required
def change_background_save(request):
    rspd = {}
    if request.method=="POST":
        client_response = request.POST['client_response']
        fn = client_response.split('=')[1][8:]
        user = request.user
        user_profile = user.get_profile()
        if user_profile.background == fn:
            rspd['msg'] = u'不可重复保存'
            res = json.dumps(rspd)
            return HttpResponse(res)
        if user_profile.pp < 100:
            rspd['msg'] = u'保存失败，你的PP不足100。'
            res = json.dumps(rspd)
            return HttpResponse(res)
        g = Gallery(user = user, imagefile = fn)
        g.save()

        user_profile.background = fn
        user_profile.pp -= 100
        user_profile.save()
        rspd['msg'] = u'保存成功'
        res = json.dumps(rspd)
        return HttpResponse(res)

@login_required
def change_introduce(request):
    rspd = {}
    if request.method=="POST":
        client_response = request.POST['client_response']
        user_profile = request.user.get_profile()
        if user_profile.pp < 100:
            rspd['msg'] = u'保存失败，你的PP不足100。'
            res = json.dumps(rspd)
            return HttpResponse(res)
        user_profile.introduce = client_response
        user_profile.pp -= 100
        user_profile.save()
        rspd['msg'] = u'保存成功'
        res = json.dumps(rspd)
        return HttpResponse(res)

@login_required
def change_password(request):
    form = ChangePasswordForm()
    word = ''
    if request.method=="POST":
        form = ChangePasswordForm(request.POST, request.FILES)
        if form.is_valid():
            username = request.user.username
            old_password = form.cleaned_data["old_password"]
            new_password = form.cleaned_data["new_password"]
            conf_password = form.cleaned_data["conf_password"]
            user = auth.authenticate(username=username,password=old_password)
            if user:
                if new_password == conf_password:
                    user.set_password(new_password)
                    user.save()
                    word = '修改成功'
                    return render_to_response("account/change_password.html",{'form': form, 'word': word}, context_instance=RequestContext(request))
                else:
                    word = '新密码不一致'
                    return render_to_response("account/change_password.html",{'form': form, 'word': word}, context_instance=RequestContext(request))
            else:
                word = '原密码不正确'
                return render_to_response("account/change_password.html",{'form': form, 'word': word}, context_instance=RequestContext(request))
    return render_to_response("account/change_password.html",{'form': form, 'word': word}, context_instance=RequestContext(request))
