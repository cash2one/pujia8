#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from forms import GameRequestForm
from models import GameRequest
import time
from django.core.cache import cache
from articles.models import Articles
from django.contrib.auth.models import User
from account.models import Profile
from games.models import Games

def Request(request):
    requestslist = GameRequest.objects.all().order_by('-add_time')
    return render_to_response('request/list.html',{'requestslist': requestslist},
                              context_instance=RequestContext(request))

def send(request):
    if request.method == 'POST':
        form = GameRequestForm(request.POST,request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            category = form.cleaned_data['category']
            gamepack = form.cleaned_data['gamepack']
            publish_time = form.cleaned_data['publish_time']
            add_time = time.strftime("%Y-%m-%d", time.localtime())
            game_type = form.cleaned_data['game_type']
            download_link = form.cleaned_data['download_link']
            introduce = form.cleaned_data['introduce']
            caption = form.cleaned_data['caption']
            ip = request.META['REMOTE_ADDR']
            up = 0
            down = 0
            name = request.user
            m = GameRequest(title=title,
                        category=category,
                        gamepack=gamepack,
                        publish_time=publish_time,
                        game_type=game_type,
                        download_link=download_link,
                        introduce=introduce,
                        caption=caption,
                        ip=ip,
                        up=up,
                        down=down,
                        name = name
                        )
            m.save()
            return HttpResponseRedirect('..')
    else:
        form = GameRequestForm()
    return render_to_response('request/send.html',{'form': form},
                              context_instance=RequestContext(request))

def show(request, rid):
    RequestGame = get_object_or_404(GameRequest, pk=rid)
    article_hot_list = cache.get('article_hot_list')
    if not article_hot_list:
        article_hot_list = Articles.objects.select_related().filter(hot='1',post='1').order_by('-time')[:10]
        cache.set('article_hot_list', article_hot_list, 900)

    request_user = User.objects.select_related().get(id=RequestGame.name_id)
    try:
        user_profile = request_user.get_profile()
    except :
        import time
        today = time.strftime("%Y-%m-%d", time.localtime())
        profile = Profile(user=request_user, count=0, today=today, todaycount=0)
        profile.save()
        user_profile = request_user.get_profile()

    game_hot_list = cache.get('game_hot_list')
    if not game_hot_list:
        game_hot_list = Games.objects.select_related().filter(post='1').order_by('-count')[:10]
        cache.set('game_hot_list', game_hot_list, 900)
    return render_to_response('request/show.html',{'RequestGame': RequestGame, \
                                           'article_hot_list': article_hot_list, 'game_hot_list': game_hot_list, \
                                           'user_profile': user_profile},
                              context_instance=RequestContext(request))

def vote(request, rid, votetype):
    if not request.user.is_authenticated():
        return HttpResponse(u'请先登录！')
    RequestGame = get_object_or_404(GameRequest, pk=rid)
    if votetype == 'up':
        RequestGame.up += 1
    if votetype =='down':
        RequestGame.down += 1
    RequestGame.save()
    return HttpResponseRedirect('/request/%s/'%rid)
