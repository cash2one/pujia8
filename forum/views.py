#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

import json,os,re
from forms import EditPostForm, NewPostForm, ForumForm
from models import Topic, Forum, Post, Seed, Score

from request.models import GameRequest
from games.models import Games
from account.models import Profile
from wish.models import Wish
from pujia_comments.models import PujiaComment
from gifts.models import Gifts
from link.models import Link

from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed

from pujia_toolkit import pujia_text, gravatar_for_user

import time
import datetime

today = time.strftime("%Y-%m-%d", time.localtime())

def recent(request, template_name="index.html"):
    ctx = {}
    ctx['games_qiuhanhua'] = Games.objects.select_related().exclude(language='cn').filter(post='1', hh=True).order_by('-week_qiuhanhua_num', '-qiuhanhua_num', '-add_time')[:10]
    # games = list(Games.objects.select_related().filter(language='cn', post='1', state='1').order_by('-publish_time', '-add_time')[:5])
    # games.extend(list(Games.objects.select_related().exclude(language='cn').filter(post='1', state='1').order_by('-publish_time', '-add_time')[:5]))
    ctx['games'] = Games.objects.select_related().filter(post='1', state='1').order_by('-publish_time', '-add_time')[:10]
    ctx['games_hhing'] = Games.objects.select_related().filter(post='1', state='2').order_by('-add_time')[:4]
    ctx['unpost_games'] = Games.objects.select_related().filter(post='1', state='0').order_by('publish_time')[:3]
    ctx['wish_games'] = Wish.objects.select_related().filter(fin = False).order_by('-add_time')
    ctx['wish_games_fin'] = Wish.objects.select_related().filter(fin = True).order_by('-add_time')[:3]
    ctx['pp_rank'] = Profile.objects.select_related().all().order_by('-pp')[:10]
    ctx['super_comment_rank'] = Profile.objects.select_related().all().order_by('-super_comment')[:10]
    ctx['gifts'] = Gifts.objects.select_related().filter(suggest = True)

    ob = request.GET.get('order_by')
    ctx['form'] = ForumForm(request.GET)
    if not ob:
        if 'order_by' in request.COOKIES:
            ob = request.COOKIES["order_by"]
        else:
            ob = '-last_reply_on'
        ctx['form'] = ForumForm(request.COOKIES)
    ctx['topics'] = Topic.objects.select_related().filter(forum__show_in_index = True).order_by('-sticky', ob)
    return render(request, template_name, ctx)

def forum(request, forum_slug, topic_type = '', topic_type2 = '', template_name="lbforum/forum.html"):
    forum = get_object_or_404(Forum, slug = forum_slug)
    topics = forum.topics.all()
    ob = request.GET.get('order_by')
    form = ForumForm(request.GET)
    if not ob:
        if 'order_by' in request.COOKIES:
            ob = request.COOKIES["order_by"]
        else:
            ob = '-last_reply_on'
        form = ForumForm(request.COOKIES)

    if topic_type:
        topic_type2 = topic_type
        topics = topics.filter(topic_type__slug = topic_type).order_by(ob).select_related()
        topic_type = ''
    else:
        topics = topics.order_by(ob).select_related()
    ext_ctx = {'form': form, 'forum': forum, 'topics': topics, 'topic_type': topic_type,  'topic_type2': topic_type2}
    return render(request, template_name, ext_ctx)

def topic(request, topic_id, template_name="lbforum/topic.html"):
    topic = get_object_or_404(Topic, id = topic_id)
    topic.num_views += 1
    topic.save()
    posts = topic.posts
    posts = posts.filter(topic_post=False).order_by('created_on').select_related()
    ext_ctx = {'topic': topic, 'posts': posts}
    return render(request, template_name, ext_ctx)

def seed(request, topic_id):
    rspd = {}
    request_user = request.user
    if not request_user.is_authenticated():
        rspd['msg'] = u'要收藏，先登录！'
        res = json.dumps(rspd)
        return HttpResponse(res)
    topic = get_object_or_404(Topic, id = topic_id)
    if topic.posted_by == request_user:
        rspd['msg'] = u'没必要收藏自己的主题哦！'
        res = json.dumps(rspd)
        return HttpResponse(res)
    seed_user = Seed.objects.filter(topic = topic, seed_by = request_user).select_related()
    if seed_user:
        rspd['msg'] = u'你已经收藏了，不能重复收藏！'
        res = json.dumps(rspd)
        return HttpResponse(res)
    else:
        seed = Seed(topic = topic, seed_by = request_user)
        seed.save()
        topic.num_seeds += 1
        topic.save()
        rspd['msg'] = u'收藏成功！'
        res = json.dumps(rspd)
        return HttpResponse(res)

def score(request, post_id):
    rspd = {}
    request_user = request.user

    post = get_object_or_404(Post, id = post_id)
    if post.posted_by == request_user:
        rspd['msg'] = u'不能宠幸自己！'
        res = json.dumps(rspd)
        return HttpResponse(res)
    score_user = Score.objects.filter(post = post, score_by = request_user).select_related()
    if score_user:
        rspd['msg'] = u'你已经宠幸过了！'
        res = json.dumps(rspd)
        return HttpResponse(res)

    pp = int(request.POST['client_response'])
    if pp == 0:
        rspd['msg'] = u'PP值不能为0，请重新输入。'
        res = json.dumps(rspd)
        return HttpResponse(res)
    request_user_profile = request_user.get_profile()
    min_score_pp = -1
    check_in_total = request_user_profile.check_in_total
    if check_in_total < 7:
        rspd['msg'] = u'你的总签到数不足7，无权限进行宠幸！'
        res = json.dumps(rspd)
        return HttpResponse(res)
    if request_user_profile.pp < 20:
        rspd['msg'] = u'你的PP少于20，无权限进行宠幸！'
        res = json.dumps(rspd)
        return HttpResponse(res)
    if 7 <= check_in_total < 14:
        max_score_pp = 1
    if 14 <= check_in_total < 100:
        max_score_pp = 3
    if 100 <= check_in_total < 365:
        min_score_pp = -2
        max_score_pp = 6
    if 365 <= check_in_total:
        min_score_pp = -3
        max_score_pp = 9

    if request_user.has_perm('forum.delete_post'):
        min_score_pp = -250
        max_score_pp = 250
    if request_user.is_superuser:
        min_score_pp = -9999
        max_score_pp = 9999

    if not min_score_pp <= pp <= max_score_pp:
        rspd['msg'] = u'超过PP上限！'
        res = json.dumps(rspd)
        return HttpResponse(res)

    score = Score(post = post, pp = pp, score_by = request_user)
    score.save()

    user_profile = post.posted_by.get_profile()
    user_profile.pp += pp
    user_profile.save()

    if not request_user.has_perm('forum.delete_post'):
        request_user_profile.pp -= abs(pp)
    request_user_profile.save()

    rspd['msg'] = u'宠幸成功！'
    res = json.dumps(rspd)
    return HttpResponse(res)

def post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return HttpResponseRedirect(post.get_absolute_url_ext())

@login_required
def new_post(request, forum_id=None, topic_id=None, form_class=NewPostForm, \
        template_name='lbforum/post.html'):
    qpost = topic = forum = first_post = None
    post_type = _('topic')
    topic_post = True
    if forum_id:
        forum = get_object_or_404(Forum, pk=forum_id)
    if topic_id:
        post_type = _('reply')
        topic_post = False
        topic = get_object_or_404(Topic, pk=topic_id)
        forum = topic.forum
        first_post = topic.posts.order_by('created_on').select_related()[0]
    user = request.user
    user_profile = user.get_profile()
    if request.method == "POST":
        rspd = {}
        if user_profile.check_in_total < 3 and user_profile.pp < 100:
            import time
            today = time.localtime()
            year, month, day = today.tm_year, today.tm_mon, today.tm_mday
            today_post_num = user.post_set.filter(created_on__year = year, created_on__month = month, created_on__day = day).count()
            if today_post_num >= 3:
                rspd['info'] = '您的总签到数不足3天或少于100PP，每天的回复不可超过3条。'
                return HttpResponse(json.dumps(rspd))
        # print 'request.POST\n', request.POST
        #print request.POST.getlist('checkbox')
        form = form_class(request.POST, user=user, forum=forum, topic=topic, \
                ip=request.META['REMOTE_ADDR'])
        if form.is_valid():
            if Post.objects.select_related().filter(message=request.POST["message"]).exists():
                rspd['info'] = '已存在相同的回复内容，请勿灌水。'
                return HttpResponse(json.dumps(rspd))
            post = form.save()
            text = post.message
            if '@' in text:
                name_list = re.findall('\@([\S]*)', text)
                for name in  name_list:
                    try:
                        at_user = User.objects.select_related().get(username__exact = name)
                        user_profile = at_user.get_profile()
                        user_profile.notification += 1
                        user_profile.save()
                    except:
                        pass

            rspd['username'] = user.username
            rspd['uid'] = user.id
            rspd['avatar'] = gravatar_for_user(user)
            rspd['cid'] = post.id
            rspd['date'] = post.created_on.strftime("%Y-%m-%d %H:%M:%S")
            rspd['content'] = pujia_text(text)
            rspd['info'] = ''
            if topic:
                return HttpResponse(json.dumps(rspd))
            else:
                return HttpResponseRedirect(reverse("lbforum_forum", args=[forum.slug]))
    else:
        if user_profile.check_in_total < 3 and user_profile.pp < 100:
            return HttpResponse('您的总签到数不足3天或少于100PP，尚无权限发表主题。')
        initial={}
        qid = request.GET.get('qid', '')
        if qid:
            qpost = get_object_or_404(Post, id=qid)
            initial['message'] = "@%s " % (qpost.posted_by.username)
        form = form_class(initial=initial, forum=forum)
    ext_ctx = {'forum':forum, 'form':form, 'topic':topic, 'first_post':first_post, \
            'post_type':post_type}
    ext_ctx['is_new_post'] = True
    ext_ctx['topic_post'] = topic_post
    ext_ctx['session_key'] = request.session.session_key
    return render(request, template_name, ext_ctx)

@login_required
def edit_post(request, post_id, form_class=EditPostForm, template_name="lbforum/post.html"):
    post_type = _('reply')
    edit_post = get_object_or_404(Post, id=post_id)
    from datetime import *
    if not (request.user.is_superuser or request.user == edit_post.posted_by):
        return HttpResponse(ugettext('no right'))
    if not request.user.has_perm('forum.delete_post') and (datetime.now() - edit_post.created_on).days > 30:
        return HttpResponse(u'很遗憾，不能编辑30天前的帖子。')
    if edit_post.topic_post:
        post_type = _('topic')
    if request.method == "POST":
        form = form_class(instance=edit_post, user=request.user, data=request.POST)
        if form.is_valid() and request.POST.get('submit', ''):
            edit_post = form.save()
            return HttpResponseRedirect('../')
    else:
        form = form_class(instance=edit_post)
    ext_ctx = {'form':form, 'post': edit_post, 'topic':edit_post.topic, \
            'forum':edit_post.topic.forum, 'post_type':post_type}
    ext_ctx['topic_post'] = edit_post.topic_post
    ext_ctx['session_key'] = request.session.session_key
    return render(request, template_name, ext_ctx)

@login_required
def user_topics(request, user_id, template_name='lbforum/account/user_topics.html'):
    view_user = User.objects.get(pk=user_id)
    topics = view_user.topic_set.order_by('-created_on').select_related()
    return render(request, template_name, {'topics': topics, 'view_user': view_user})

@login_required
def user_posts(request, user_id, template_name='lbforum/account/user_posts.html'):
    view_user = User.objects.get(pk=user_id)
    posts = view_user.post_set.order_by('-created_on').select_related()
    return render(request, template_name, {'posts': posts, 'view_user': view_user})

@login_required
def user_at(request, user_id, template_name='lbforum/account/user_at.html'):
    view_user = User.objects.get(pk=user_id)
    if request.user != view_user:
        return HttpResponse(ugettext('no right'))
    user_profile = view_user.get_profile()
    user_profile.notification = 0
    user_profile.save()
    posts = Post.objects.filter(Q(message__contains = '@%s '%view_user.username) | Q(message__contains = '@%s\n'%view_user.username)).order_by('-created_on').select_related()[:30]
    comments = PujiaComment.objects.filter(content__contains = '@%s'%view_user.username).order_by('-date').select_related()[:30]
    return render(request, template_name, {'posts': posts, 'view_user': view_user, 'comments': comments})

@login_required
def user_seeds(request, user_id, template_name='lbforum/account/user_seeds.html'):
    if request.method == 'POST':
        tids = request.POST.getlist('tid')
        tids = [int(tid) for tid in tids]
        Seed.objects.filter(topic__id__in = tids, seed_by = request.user).delete()
        return HttpResponseRedirect('.')
    else:
        view_user = User.objects.get(pk=user_id)
        if request.user != view_user:
            return HttpResponse(ugettext('no right'))
        seed_list = view_user.seed_set.order_by('-id').values_list('topic_id', flat=True)
        topics = Topic.objects.select_related().filter(id__in = seed_list)
        return render(request, template_name, {'topics': topics, 'view_user': view_user})

@login_required
def delete_topic(request, topic_id):
    if not request.user.is_superuser:
        return HttpResponse(ugettext('no right'))
    topic = get_object_or_404(Topic, id = topic_id)
    forum = topic.forum
    topic.delete()
    forum.update_state_info()
    return HttpResponseRedirect(reverse("lbforum_forum", args=[forum.slug]))

@login_required
def delete_post(request, post_id):
    if not request.user.has_perm('forum.delete_post'):
        return HttpResponse(ugettext('no right'))
    post = get_object_or_404(Post, id=post_id)
    topic = post.topic
    post.delete()
    topic.update_state_info()
    topic.forum.update_state_info()
    return HttpResponseRedirect(reverse("lbforum_topic", args=[topic.id])+'?page=%s#comments'%((topic.num_replies - 2)/15 + 1))

@login_required
def update_topic_attr_as_not(request, topic_id, attr):
    if not request.user.has_perm('forum.delete_topic'):
        return HttpResponse(ugettext('no right'))
    topic = get_object_or_404(Topic, id = topic_id)
    if attr == 'sticky':
        topic.sticky = not topic.sticky
    elif attr == 'close':
        topic.closed = not topic.closed
    elif attr == 'hide':
        topic.hidden = not topic.hidden
        u = topic.posted_by.get_profile()
        u.pp -= topic.forum.pp_topic
        u.save()
    elif attr == 'distillate':
        topic.level = 30 if topic.level >= 60 else 60
    topic.save()
    if topic.hidden:
        return HttpResponseRedirect(reverse("lbforum_forum", args=[topic.forum.slug]))
    else:
        return HttpResponseRedirect(reverse("lbforum_topic", args=[topic.id]))

enable_ext = ['.jpg', '.jpeg', '.gif', '.png', '.bmp', '.zip', '.rar', '.gz', '.7z', '.apk', '.ipa', '.mp3']
img_ext = ['.jpg', '.jpeg', '.png', '.bmp']

@csrf_exempt
def upload(request):
    rspd = {}
    if request.method=="POST":
        url_list = []
        for file_obj in request.FILES.getlist('filetoupload'):
            if file_obj.size > 3145728:
                rspd['status'] = 503
                rspd['msg'] = u'不能上传超过3M大小的文件，请上传至网盘'
                rspd['errors'] = u'不能上传超过3M大小的文件，请上传至网盘'
                res = json.dumps(rspd)
                return HttpResponse(res)
            ext = os.path.splitext(file_obj.name)[1].lower()
            if ext not in enable_ext:
                rspd['status'] = 503
                rspd['msg'] = u'不允许上传此类型的文件'
                rspd['errors'] = u'不允许上传此类型的文件'
                res = json.dumps(rspd)
                return HttpResponse(res)

            import time, random
            fn = time.strftime('%Y%m%d%H%M%S')
            fn = fn + '_%d' %random.randint(0,100)

            if ext in img_ext:
                if 'upload_to' in request.POST:
                    url = 'static/%s/%s.jpg'%(request.POST['upload_to'], fn) #avatars
                else:
                    url = 'static/upload/%s.jpg'%fn
                from PIL import ImageFile, Image
                parser = ImageFile.Parser()
                for chunk in file_obj.chunks():
                    parser.feed(chunk)
                img = parser.close()
                width, heigth = img.size
                if width * 16 / heigth <= 9:
                    img = img.resize((600*width/heigth, 600),  Image.ANTIALIAS)
                elif width > 800:
                    img = img.resize((800, 800*heigth/width),  Image.ANTIALIAS)
                img.convert(mode='RGB').save(url, quality = 90)
            else:
                url = 'static/upload/%s%s'%(fn,ext)
                destination = open(url, 'wb+')
                for chunk in file_obj.chunks():
                    destination.write(chunk)
                destination.close()

            url_list.append('/'+url)
        rspd['status'] = 200
        rspd['msg'] = u'成功上传'
        rspd['url'] = ' '.join(url_list)
        res = json.dumps(rspd)
        return HttpResponse(res)

def search(request, template_name='search.html'):
    word = request.GET.get('w')
    if word:
        topics = Topic.objects.select_related().filter(subject__icontains = word)
        games = Games.objects.select_related().filter(Q(post='1'),Q(title_cn__icontains = word))
        requests = GameRequest.objects.select_related().filter(Q(title__icontains = word))
        return render(request, template_name, {'topics': topics, 'games': games, 'requests': requests, 'word': word})
    else:
        return HttpResponseRedirect('/')

def robots(request):
    return HttpResponse('User-agent: Sosospider<br>Disallow: /<br>User-agent: Sogou web spider<br>Disallow: /<br>User-agent: sogou spider<br>Disallow: /<br>User-agent: YodaoBot<br>Disallow: /<br>User-agent: *<br>Disallow:<br>Crawl-delay: 60')

def crontab(request):
    Profile.objects.select_related().all().update(todaycount = 0, today_score_times = 0)
    Link.objects.select_related().all().update(todaycount = 0)
    return HttpResponse('done')

def crontab_month(request):
    Link.objects.select_related().all().update(monthcount = 0)
    return HttpResponse('done')

def crontab_week(request):
    Games.objects.select_related().all().update(week_qiuhanhua_num = 0)
    return HttpResponse('done')