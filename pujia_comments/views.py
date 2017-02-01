#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from models import PujiaComment, CommentPositive
from forms import EditCommentForm
from django.core.cache import cache
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import re, json, time
from pujia_toolkit import pujia_text, gravatar_for_user

def post_comment(request):
    if request.method == 'POST':
        rspd = {}
        comment_user = request.user
        target = request.POST['path']
        content = request.POST['comment']

        if len(content) < 10:
            return HttpResponse('no spam!')

        if PujiaComment.objects.select_related().filter(content=content).exists():
            rspd['info'] = '请勿重复提交。'
            return HttpResponse(json.dumps(rspd))

        next = request.POST['next']+'#comments'
        c = PujiaComment(name=comment_user, target=target, content=content)
        c.save()

        if '@' in content:
            name_list = re.findall('\@([\S]*)', content)
            for name in  name_list:
                try:
                    user = User.objects.select_related().get(username__exact = name)
                    user_profile = user.get_profile()
                    user_profile.notification += 1
                    user_profile.save()
                except:
                    pass

        rspd['info'] = ''
        rspd['username'] = comment_user.username
        rspd['uid'] = comment_user.id
        rspd['avatar'] = gravatar_for_user(comment_user)
        rspd['cid'] = c.id
        rspd['date'] = c.date.strftime("%Y-%m-%d %H:%M:%S")
        rspd['content'] = pujia_text(content)
        return HttpResponse(json.dumps(rspd))

def delete_comment(request, cid):
    if not request.user.is_superuser:
        return HttpResponse('no right')
    comment = get_object_or_404(PujiaComment, id=cid)
    next = comment.target+'#comments'
    comment.delete()
    return HttpResponseRedirect(next)

def hot_comment(request, cid):
    if not request.user.is_superuser:
        return HttpResponse('no right')
    comment = get_object_or_404(PujiaComment, id=cid)
    next = comment.target+'#comments'
    comment.hot = True
    comment.positive = 5
    comment.save()

    u = comment.name.get_profile()
    u.pp += 20
    u.super_comment += 1
    u.save()
    return HttpResponseRedirect(next)

def add_positive(request, cid):
    comment = get_object_or_404(PujiaComment, id=cid)
    if comment.name == request.user:
        return HttpResponse(u'不能赞自己的评论。')
    if CommentPositive.objects.select_related().filter(user=request.user, comment=comment).exists():
        return HttpResponse(u'你已赞过此条评论。')
    next = comment.target+'#comments'
    cp = CommentPositive(user=request.user, comment=comment)
    cp.save()
    return HttpResponseRedirect(next)

def hot_comments_list(request, template_name="pujia_comments/show_hot_comments_list.html"):
    hot_comments = PujiaComment.objects.select_related().filter(hot=True).order_by('-date')
    return render(request, template_name, {'comments': hot_comments})

@login_required
def edit_comment(request, cid, form_class=EditCommentForm, template_name="pujia_comments/edit_comment.html"):
    edit_comment = get_object_or_404(PujiaComment, id=cid)
    if not (request.user.is_superuser or request.user == edit_comment.name):
        return HttpResponse(ugettext('no right'))
    if request.method == "POST":
        form = form_class(instance=edit_comment, data=request.POST)
        if form.is_valid():
            edit_comment.content = request.POST['content']
            edit_comment.save()
            return HttpResponseRedirect(edit_comment.target+'#comments')
    else:
        form = form_class(instance=edit_comment)
    ext_ctx = {'form':form, 'edit_comment':edit_comment}
    ext_ctx['session_key'] = request.session.session_key
    return render(request, template_name, ext_ctx)
