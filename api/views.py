# -*- coding:utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from easy_thumbnails.files import get_thumbnailer
from django.contrib.flatpages.models import FlatPage
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from forum.models import Topic, Category, Forum, Post, TopicType
from games.models import Games, Platform, QiuHanHua, GameCollection
from pujia_comments.models import PujiaComment, CommentPositive
from flow.models import *
from account.models import Profile
from gallery_app.models import GalleryApp
from gallery.models import Gallery
from adm.models import Game_ads
from gifts.models import Gifts, Cdkeys_Record
from emoji.models import Emoji, Emoji_img

from tagging.models import Tag, TaggedItem
from tokenapi.decorators import token_required
from tokenapi.http import JsonResponse, JsonError
import json, re, time, random, os, urllib2, datetime
from bs4 import BeautifulSoup
from base64 import b64encode, b64decode

domain = 'http://www.pujia8.com'

options = {'size': (150, 150), 'quality': 85}
options2 = {'size': (360, 480), 'quality': 90, 'crop': True}

options_small = {'size': (216, 142), 'quality': 85, 'crop': True}
options_large = {'size': (660, 328), 'quality': 85, 'crop': True}
options_avatar = {'size': (48, 48), 'quality': 85, 'crop': True}

language_dic = {u'cn': u'中文', u'en': u'英文', u'jp': u'日文'}

ads = [
    {'url': 'http://www.pujia8.com/library/9198/',
     'img_h': 'http://www.pujia8.com/static/uploads/20161208140709_79.jpg',
     'img_v': 'http://www.pujia8.com/static/uploads/20161214174620_81.jpg',
     'package': '',
     'name': u'造物法则',
     'weight': 3},
    {'url': 'http://ma20.gdl.netease.com/ma20_netease_netease.pujia8_cps_dev_1.1.76.apk',
     'img_h': 'http://www.pujia8.com/static/uploads/20170107224042_75.jpeg',
     'img_v': 'http://www.pujia8.com/static/uploads/20170107224022_70.jpg',
     'package': 'com.netease.ycyzj',
     'name': u'大富翁9',
     'weight': 10},
    {'url': 'http://www.pujia8.com/link/68/',
     'img_h': 'http://www.pujia8.com/static/uploads/20161011225753_66.jpg',
     'img_v': 'http://www.pujia8.com/static/uploads/20161011230202_75.jpeg',
     'package': '',
     'name': u'FGO',
     'weight': 3},
    {'url': 'http://www.pujia8.com/link/69/',
     'img_h': 'http://www.pujia8.com/static/uploads/20161019143735_18.jpeg',
     'img_v': 'http://www.pujia8.com/static/uploads/20161019143522_42.jpeg',
     'package': '',
     'name': u'契约勇士',
     'weight': 3},
    {'url': 'http://www.pujia8.com/link/60/',
     'img_h': 'http://www.pujia8.com/static/uploads/20160908190537_3.jpg',
     'img_v': 'http://www.pujia8.com/static/uploads/20160908190455_6.jpg',
     'package': '',
     'name': u'阴阳师',
     'weight': 6}
]

# @cache_page(60 * 30)
def get_games_setting(request, package):
    rspd = {}
    channel = request.GET.get('channel', 'pj')
    rspd['package'] = package
    rspd['adview_key'] = ''
    rspd['patch_url'] = ''
    rspd['adsdk'] = 0
    rspd['install_yipiao'] = False
    rspd['install_pujia8'] = True
    rspd['install_pujia8_url'] = 'https://d.pujia8.com/apk/com.pujia8.app_1.6.apk'
    # if channel in ['pj'] and package in ["air.jp.globalgear.city.pj", "tokyo.seec.yotumegami.pj"]:
    #     rspd['install_pujia8'] = True

    ads_full = []
    for ad in ads:
        ads_full.extend([ad for i in range(ad['weight'])])
    pujia_ad = random.choice(ads_full)

    rspd['pujia_ad'] = pujia_ad
    if Game_ads.objects.select_related().filter(package = package, channel = channel).exists():
        game_ads = Game_ads.objects.select_related().filter(package = package, channel = channel)[0]
        rspd['timespan'] = game_ads.timespan
        rspd['sms'] = game_ads.sms
        rspd['banner'] = game_ads.banner
        rspd['inst'] = game_ads.inst
        rspd['splash'] = game_ads.splash
        rspd['pujiasdk'] = game_ads.pujiasdk
        rspd['VersionCode'] = game_ads.VersionCode
        rspd['patch_url'] = game_ads.patch_url
    else:
        banner = 6
        inst = 6
        splash = 2
        timespan = 5
        sms = False
        pujiasdk = True
        VersionCode = 21
        adview_key = 'SDK201610121004275bvzxb5ml6sxjng'
        if channel == 'hack':
            banner = inst = splash = 2
            timespan = 0
        if channel == 'mz':
            timespan = 0
        if channel == 'zy':
            banner = inst = splash = 0
        if channel == 'xm':
            timespan = 5
            banner = inst = splash = 5
        if channel == 'pj':
            timespan = 0
            sms = False
        if channel in [u'pj', u'hack', u'wdj', u'wdjlx', u'xx', u'dl', u'qh', u'zy', u'mmy', u'yyb', u'hw', u'mz', u'xm', u'az']:
            game_ads = Game_ads(package = package, channel= channel, banner = banner, inst = inst, splash = splash, timespan = timespan, sms = sms, pujiasdk = pujiasdk, VersionCode = VersionCode, adview_key = adview_key)
            game_ads.save()
        rspd['timespan'] = timespan
        rspd['sms'] = sms
        rspd['banner'] = banner
        rspd['inst'] = inst
        rspd['splash'] = splash
        rspd['pujiasdk'] = pujiasdk
        rspd['VersionCode'] = VersionCode
    return JsonResponse(rspd)

def gravatar_for_user(user):
    if user:
        avatar_url = cache.get('avatar_url_uid%s'%user.id)
        if not avatar_url:
            avatar = user.get_profile().avatar
            if avatar:
                options = {'size': (80, 80), 'quality': 85, 'crop': True}
                avatar_url = get_thumbnailer(avatar.url[8:]).get_thumbnail(options).url
            else:
                avatar_url = '/static/img/tx.jpg'
            cache.set('avatar_url_uid%s'%user.id, avatar_url, 1800)
    else:
        avatar_url = '/static/img/tx.jpg'
    return avatar_url

def get_head_img(topic_id):
    head_img = cache.get('get_head_img_topic_%d'%topic_id)
    if not head_img:
        gallerys = Gallery.objects.select_related().all()
        gallery = random.choice(gallerys)
        head_img = gallery.imagefile.url
        cache.set('get_head_img_topic_%d'%topic_id, head_img, 315360000)
    return head_img[8:]

def topic2json(topic):
    t = {}
    t['topic_id'] = topic.id
    t['subject'] = topic.subject
    t['num_views'] = topic.num_views
    t['num_replies'] = topic.num_replies-1
    t['created_on'] = str(topic.created_on)
    last_reply_on = topic.last_reply_on.strftime("%Y-%m-%d %H:%M:%S")
    t['last_reply_on'] = last_reply_on
    t['last_reply_on_mktime'] = int(time.mktime(time.strptime(last_reply_on, '%Y-%m-%d %H:%M:%S')))
    t['user_gravatar'] = gravatar_for_user(topic.posted_by)
    t['user_name'] = topic.posted_by.username
    t['user_info'] = get_user_info(topic.posted_by)['user_info']
    pics_list = re.findall('/static/[a-zA-z0-9/\.]+[jpg|JPG|jpeg|JPEG|png|PNG|gif|GIF]',
                           topic.posts.filter(topic_post=True)[0].message)
    pics_list = [pic for pic in pics_list if 'emoji' not in pic or '.gif' not in pic or '.GIF' not in pic or pic != u'/static/up']
    if pics_list:
        head_img = pics_list[-1][8:]
    else:
        head_img = get_head_img(topic.id)
    try:
        t['head_img'] = get_thumbnailer(head_img).get_thumbnail(options_large).url
    except:
        t['head_img'] = '/static/pics/ac20007d581324bcd36.jpg'
    try:
        if len(pics_list) >= 3:
            pics_list = [get_thumbnailer(p[8:]).get_thumbnail(options_small).url for p in pics_list[:3]]
            show_type = '3'
        elif len(pics_list) == 0:
            show_type = 'n'
        else:
            pics_list = [get_thumbnailer(p[8:]).get_thumbnail(options_small).url for p in pics_list[:1]]
            show_type = '0'
    except:
        pics_list = []
        show_type = 'n'
    t['pics_list'] = pics_list
    t['show_type'] = show_type
    return t

def topics2json(topics):
    topics_list = []
    for topic in topics:
        topics_list.append(topic2json(topic))
    return topics_list

def get_topics_list(request, forum_id = None, type_id = None):
    since_id = request.GET.get('since_id')
    max_id = request.GET.get('max_id')
    since_time = request.GET.get('since_time')
    max_time = request.GET.get('max_time')
    topics = Topic.objects.select_related().filter(forum__show_in_index=True).order_by('-last_reply_on')
    if forum_id:
        topics = topics.filter(forum_id=forum_id)
    if type_id:
        topics = topics.filter(topic_type_id=type_id)
    if since_id:
        since_id = int(since_id)
        topics = topics.filter(id__lt = since_id)
    if max_id:
        max_id = int(max_id)
        topics = topics.filter(id__gt = max_id).order_by('created_on')
    if since_time:
        since_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(since_time)))
        topics = topics.filter(last_reply_on__lt=since_time).order_by('-last_reply_on')
    if max_time:
        max_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(int(max_time) + 1)))
        topics = topics.filter(last_reply_on__gt=max_time).order_by('last_reply_on')

    rspd = {'code': 200, 'version': 0.1, 'topics_list': topics2json(topics[:15])}
    return JsonResponse(rspd)

def view_topic(request, tid):
    topic = get_object_or_404(Topic, id = tid)
    posts = topic.posts.select_related()

    t = topic2json(topic)
    t['content'] = posts.get(topic_post=True).message

    rspd = {'code': 200, 'version': 0.1, 'topic': t}
    return JsonResponse(rspd)

#old
def get_topic_comments(request, tid):
    topic = get_object_or_404(Topic, id = tid)
    posts = topic.posts.select_related()

    since_id = request.GET.get('since_id')
    max_id = request.GET.get('max_id')
    if since_id:
        since_id = int(since_id)
        posts = posts.filter(id__lt = since_id, topic_post=False).order_by('created_on')[:15]
    elif max_id:
        max_id = int(max_id)
        posts = posts.filter(id__gt = max_id, topic_post=False).order_by('created_on')[:15]
    else:
        posts = posts.filter(topic_post=False).order_by('created_on')[:15]

    posts_list = []
    for post in posts:
        p = {}
        p['comment_id'] = post.id
        p['user_name'] = post.posted_by.username
        p['user_gravatar'] = gravatar_for_user(post.posted_by)
        p['user_info'] = get_user_info(post.posted_by)['user_info']
        p['created_on'] = str(post.created_on)
        p['content'] = post.message
        posts_list.append(p)

    rspd = {'code': 200, 'version': 0.1, 'num_replies': topic.num_replies-1, 'posts_list': posts_list}
    return JsonResponse(rspd)

def get_topic_comments2(request, tid):
    topic = get_object_or_404(Topic, id = tid)
    posts = topic.posts.select_related()

    since_id = request.GET.get('since_id')
    max_id = request.GET.get('max_id')
    if since_id:
        since_id = int(since_id)
        posts = posts.filter(id__lt = since_id, topic_post=False).order_by('-id')[:15]
    elif max_id:
        max_id = int(max_id)
        posts = posts.filter(id__gt = max_id, topic_post=False).order_by('id')[:15]
    else:
        posts = posts.filter(topic_post=False).order_by('-id')[:15]

    posts_list = []
    for post in posts:
        p = {}
        p['comment_id'] = post.id
        p['user_info'] = get_user_info(post.posted_by)['user_info']
        p['created_on'] = str(post.created_on)
        p['content'] = post.message
        posts_list.append(p)

    rspd = {'code': 200, 'version': 0.1, 'num_replies': topic.num_replies-1, 'posts_list': posts_list}
    return JsonResponse(rspd)

def game2json(game, platform = None):
    t = {}
    t['game_id'] = game.id
    t['icon'] = get_thumbnailer(game.imagefile).get_thumbnail(options).url
    t['title_cn'] = game.title_cn
    t['type'] = game.tags
    t['size'] = game.game_size
    if game.versionName:
        t['versionName'] = game.versionName
    else:
        t['versionName'] = ''
    t['pack'] = game.package
    pub_time = game.add_time.strftime("%Y-%m-%d %H:%M:%S")
    t['pub_time'] = pub_time
    t['pub_mktime'] = int(time.mktime(time.strptime(pub_time, '%Y-%m-%d %H:%M:%S')))
    t['language'] = language_dic[game.language]
    t['num_views'] = game.count
    t['qiuhanhua_num'] = game.qiuhanhua_num
    t['hot'] = game.hot
    if 'http' in game.apk_name:
        t['apk_link'] = game.apk_name
    else:
        t['apk_link'] = 'https://d.pujia8.com/apk/%s' % (game.apk_name)
    if game.obb_name:
        t['obb'] = True
        if 'http' in game.obb_name:
            t['obb_link'] = game.obb_name
            obb_name = game.obb_name.split('/')[-1]
            t['obb_path'] = '/Android/obb/%s/%s' % (game.package, obb_name)
        else:
            t['obb_link'] = 'https://d.pujia8.com/obb/%s' % (game.obb_name)
            t['obb_path'] = '/Android/obb/%s/%s' % (game.package, game.obb_name)
    else:
        t['obb'] = False
    #以下模拟器游戏用
    if platform:
        t['apk_link'] = 'https://d.pujia8.com/%s/%s'%(platform, game.emu_game_name)
        t['pack'] = game.emu_game_code
        t['versionName'] = platform.upper()
    return t

def games2json(games, platform = None):
    games_list = []
    for game in games:
        games_list.append(game2json(game, platform))
    return games_list

def get_games_list(request):
    since_time = request.GET.get('since_time')
    max_time = request.GET.get('max_time')
    language = request.GET.get('language')
    if language:
        games = Games.objects.select_related().exclude(apk_name = None).exclude(apk_name = '').filter(platform = 8, language=language, post='1').order_by('-add_time')
    else:
        games = Games.objects.select_related().exclude(apk_name = None).exclude(apk_name = '').filter(platform = 8, post='1').order_by('-add_time')
    if since_time:
        since_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(since_time)))
        games = games.filter(add_time__lt = since_time).order_by('-add_time')
    if max_time:
        max_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(int(max_time)+1)))
        games = games.filter(add_time__gt = max_time).order_by('add_time')
    rspd = {}
    rspd['code'] = 200
    rspd['version'] = 0.1
    rspd['games_list'] = games2json(games[:15])
    return JsonResponse(rspd)

def get_emu_games_list(request):
    since_time = request.GET.get('since_time')
    max_time = request.GET.get('max_time')
    pf = request.GET.get('platform', 'gba')
    platform = Platform.objects.select_related().get(platform = pf.upper())
    games = Games.objects.select_related().exclude(emu_game_code = None).exclude(emu_game_code = '').filter(platform = platform.id, post='1').order_by('-add_time')
    if since_time:
        since_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(since_time)))
        games = games.filter(add_time__lt = since_time).order_by('-add_time')
    if max_time:
        max_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(int(max_time)+1)))
        games = games.filter(add_time__gt = max_time).order_by('add_time')
    rspd = {
        'games_list': games2json(games[:15], pf)
    }
    return JsonResponse(rspd)

def get_hot_games_list(request):
    since_time = request.GET.get('since_time')
    max_time = request.GET.get('max_time')
    language = request.GET.get('language')
    if language:
        games = Games.objects.select_related().exclude(apk_name = None).exclude(apk_name = '').filter(platform = 8, language=language, post='1', hot = '1').order_by('-add_time')
    else:
        games = Games.objects.select_related().exclude(apk_name = None).exclude(apk_name = '').filter(platform = 8, post='1', hot = '1').order_by('-add_time')
    if since_time:
        since_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(since_time)))
        games = games.filter(add_time__lt = since_time).order_by('-add_time')
    if max_time:
        max_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(int(max_time)+1)))
        games = games.filter(add_time__gt = max_time).order_by('add_time')
    rspd = {}
    rspd['code'] = 200
    rspd['version'] = 0.1
    rspd['games_list'] = games2json(games[:15])
    return JsonResponse(rspd)

def get_games_tag(request, game_tag):
    game_tag = Tag.objects.get(name = game_tag)
    since_time = request.GET.get('since_time')
    max_time = request.GET.get('max_time')
    language = request.GET.get('language')
    if language:
        games = Games.objects.select_related().exclude(apk_name = None).exclude(apk_name = '').filter(platform = 8, language=language, post='1').order_by('-add_time')
    else:
        games = Games.objects.select_related().exclude(apk_name = None).exclude(apk_name = '').filter(platform = 8, post='1').order_by('-add_time')
    if since_time:
        since_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(since_time)))
        games = TaggedItem.objects.get_by_model(games.filter(add_time__lt = since_time).order_by('-add_time'), game_tag)[:15]
    elif max_time:
        max_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(int(max_time)+1)))
        games = TaggedItem.objects.get_by_model(games.filter(add_time__gt = max_time).order_by('add_time'), game_tag)[:15]
    else:
        games = TaggedItem.objects.get_by_model(games, game_tag)[:15]
    rspd = {'code': 200, 'version': 0.1, 'games_list': games2json(games)}
    return JsonResponse(rspd)

#old
@cache_page(60 * 15)
def game_timely_refresh(request, gid):
    rspd = {'code': 200, 'version': 0.1, 'num_views': 99999, 'num_comments': 99999}
    return JsonResponse(rspd)

@csrf_exempt
def check_game_install(request):
    if request.method == "POST":
        game_list = json.loads(request.POST['game_list'])
        t = []
        for package in game_list:
            games = Games.objects.select_related().filter(package = package)
            if games.exists():
                tmp = {
                    'id': games[0].pk,
                    'package': package,
                    'versionName': games[0].versionName,
                    'name': games[0].title_cn,
                    'image': get_thumbnailer(games[0].imagefile).get_thumbnail(options).url
                }
                t.append(tmp)
        rspd = {'result': t}

        if 'gba_list' in request.POST:
            gba_game_list = json.loads(request.POST['gba_list'])
            t = []
            for emu_game_code in gba_game_list:
                games = Games.objects.select_related().filter(emu_game_code=emu_game_code)
                if games.exists():
                    tmp = {
                        'id': games[0].pk,
                        'package': emu_game_code,
                        'versionName': 'GBA',
                        'name': games[0].title_cn,
                        'image': get_thumbnailer(games[0].imagefile).get_thumbnail(options).url
                    }
                    t.append(tmp)
            rspd['gba_list'] = t

        if 'nds_list' in request.POST:
            nds_game_list = json.loads(request.POST['nds_list'])
            t = []
            for emu_game_code in nds_game_list:
                games = Games.objects.select_related().filter(emu_game_code=emu_game_code)
                if games.exists():
                    tmp = {
                        'id': games[0].pk,
                        'package': emu_game_code,
                        'versionName': 'NDS',
                        'name': games[0].title_cn,
                        'image': get_thumbnailer(games[0].imagefile).get_thumbnail(options).url
                    }
                    t.append(tmp)
            rspd['nds_list'] = t

        if 'psp_list' in request.POST:
            psp_game_list = json.loads(request.POST['psp_list'])
            t = []
            for emu_game_code in psp_game_list:
                games = Games.objects.select_related().filter(emu_game_code=emu_game_code)
                if games.exists():
                    tmp = {
                        'id': games[0].pk,
                        'package': emu_game_code,
                        'versionName': 'PSP',
                        'name': games[0].title_cn,
                        'image': get_thumbnailer(games[0].imagefile).get_thumbnail(options).url
                    }
                    t.append(tmp)
            rspd['psp_list'] = t

        if 'gba_list' in request.POST or  'nds_list' in request.POST or 'psp_list' in request.POST:
            platform = Platform.objects.select_related().get(platform='GBA')
            games = Games.objects.select_related().exclude(emu_game_code=None).exclude(emu_game_code='').filter(
                platform=platform.id, post='1').order_by('-add_time')[:3]
            rspd['gba_hot_list'] = games2json(games, 'gba')

            platform = Platform.objects.select_related().get(platform='NDS')
            games = Games.objects.select_related().exclude(emu_game_code=None).exclude(emu_game_code='').filter(
                platform=platform.id, post='1').order_by('-add_time')[:3]
            rspd['nds_hot_list'] = games2json(games, 'nds')

            platform = Platform.objects.select_related().get(platform='PSP')
            games = Games.objects.select_related().exclude(emu_game_code=None).exclude(emu_game_code='').filter(
                platform=platform.id, post='1').order_by('-add_time')[:3]
            rspd['psp_hot_list'] = games2json(games, 'psp')

            platform = Platform.objects.select_related().get(platform='Android')
            games = Games.objects.select_related().exclude(package=None).exclude(package='').filter(
                platform=platform.id, post='1').order_by('-add_time')[:3]
            rspd['android_hot_list'] = games2json(games)
        return JsonResponse(rspd)
    else:
        return JsonError("hello")

@token_required
def game_qhh(request, game_id):
    user = request.user
    if not user.is_authenticated():
        return JsonError("求汉化前请先登录！")
    game = get_object_or_404(Games, id=game_id)
    qhh_date = time.strftime("%Y-%m-%d", time.localtime())
    if QiuHanHua.objects.select_related().filter(game = game, user = user, qhh_date = qhh_date).exists():
        return JsonError("你今天已经求过了，请明天再来，或者推荐好友来求汉化吧！")
    qiuhanhua = QiuHanHua(game = game, user = user, qhh_date = qhh_date)
    qiuhanhua.save()
    game.qiuhanhua_num += 1
    game.week_qiuhanhua_num += 1
    game.save(update_fields=['qiuhanhua_num', 'week_qiuhanhua_num'])
    up = user.get_profile()
    if up.pp < 5:
        return JsonError("你的PP不足")
    up.pp -= 5
    up.save(update_fields=['pp'])
    rspd = {
        'msg': '请求已发送，耗费5PP\n据说达到500就会汉化哦',
        'qiuhanhua_num': game.qiuhanhua_num
    }
    return JsonResponse(rspd)

@cache_page(60 * 30)
def game_qhh_rank(request):
    # date1 = datetime.date.today()
    # two_week = date1 - datetime.timedelta(days=60)
    games = Games.objects.select_related().exclude(language='cn').exclude(package=None).exclude(package='').filter(platform = 8, post='1', hh=True).order_by('-week_qiuhanhua_num', '-qiuhanhua_num', '-add_time')[:30]
    rspd = {
        'games_list': games2json(games)
    }
    return JsonResponse(rspd)

def view_game(request, package):
    rspd = {}
    game = Games.objects.select_related().filter(package=package)[0]
    t = game2json(game)
    t['id'] = game.id
    t['created_on'] = str(game.add_time)
    t['num_comments'] = game.comments_count
    t['content'] = game.introduce
    if game.versionName:
        t['versionName'] = game.versionName
    else:
        t['versionName'] = ''
    images_list = re.findall('(/static/[\S]*.[jpg|jpeg|png])', game.content)
    t['images_list'] = images_list
    try:
        t['head_img'] = get_thumbnailer(images_list[0][8:]).get_thumbnail(options_large).url
    except:
        t['head_img'] = '/static/pics/ac20007d581324bcd36.jpg'
    if game.review_id:
        post = Post.objects.select_related().get(topic__id = game.review_id, topic_post = True)
        t['review'] = True
        t['review_content'] = post.message
    else:
        t['review'] = False
    if game.gospel_id:
        post = Post.objects.select_related().get(topic__id = game.gospel_id, topic_post = True)
        t['gospel'] = True
        t['gospel_content'] = post.message
    else:
        t['gospel'] = False

    gifts = Gifts.objects.select_related().filter(url='/library/%d/' % game.id, post= True)
    if gifts.exists():
        t['gift'] = True
        l = []
        for gift in gifts:
            l.append(
                {
                    'gift_id': gift.id,
                    'subject': gift.subject,
                    'description': gift.description,
                    'pp': gift.pp,
                    'times': gift.times,
                    'remain_num': gift.cdkeys.all().count(),
                    'key': ''
                }
            )
        t['gift_list'] = l
    else:
        t['gift'] = False

    game.count += 1
    game.save(update_fields = ['count'])

    rspd['code'] = 200
    rspd['version'] = 0.1
    rspd['game'] = t
    rspd['comments_list'] = []
    return JsonResponse(rspd)

def view_emu_game(request, game_code):
    pf = request.GET.get('platform', 'gba')
    game = Games.objects.select_related().filter(emu_game_code=game_code)[0]
    t = game2json(game, pf)
    t['id'] = game.id
    t['created_on'] = str(game.add_time)
    t['num_comments'] = game.comments_count
    t['content'] = game.introduce
    images_list = re.findall('(/static/[\S]*.[jpg|jpeg|png])', game.content)
    t['images_list'] = images_list
    game.count += 1
    game.save(update_fields = ['count'])
    rspd = {
        'game': t
    }
    return JsonResponse(rspd)

@token_required
def gift_exchange(request, gift_id):
    user = request.user
    user_profile = user.get_profile()
    gift = Gifts.objects.select_related().get(pk = gift_id)
    if gift.cdkeys.all().count() == 0:
        return JsonError(u'此礼包已被领光。')
    elif user_profile.check_in < gift.days and user_profile.check_in_total < 30:
        return JsonError(u'需连签数大于%d天或者总签数大于30天，才能抽此礼包。'%gift.days)
    elif user_profile.pp < gift.pp:
        return JsonError(u'你的PP不足。')
    elif Cdkeys_Record.objects.select_related().filter(gifts=gift, user=user).exists():
        return JsonError(u'你已经拿过此礼包了。')
    elif random.randint(1, 10000) <= int(gift.rate):
        cdkeys = gift.cdkeys.all()
        cdkey = random.choice(cdkeys)
        key = cdkey.cdkey
        msg = key

        if key[:2] == 'pp':
            user_profile.pp += int(key[2:])

        user_profile.pp -= gift.pp
        user_profile.save()

        cr = Cdkeys_Record(gifts=gift, user=user, cdkey=cdkey.cdkey)
        cr.save()
        cdkey.delete()

        gift.times += 1
        gift.save(update_fields = ['times'])
    else:
        user_profile.pp -= gift.pp
        user_profile.save(update_fields = ['pp'])
        msg = u'很遗憾未抽中。'
        gift.times += 1
        gift.save(update_fields = ['times'])
    rspd = {
        'msg': msg
    }
    return JsonResponse(rspd)

@token_required
def gift_inquire(request, package):
    game = get_object_or_404(Games, package=package)
    gifts = Gifts.objects.select_related().filter(url='/library/%d/' % game.id, post=True)
    t = {}
    if gifts.exists():
        t['gift'] = True
        l = []
        for gift in gifts:
            cr = Cdkeys_Record.objects.select_related().filter(gifts=gift, user=request.user)
            key = ''
            if cr.exists():
                key = cr[0].cdkey
            l.append(
                {
                    'gift_id': gift.id,
                    'subject': gift.subject,
                    'description': gift.description,
                    'pp': gift.pp,
                    'times': gift.times,
                    'remain_num': gift.cdkeys.all().count(),
                    'key': key
                }
            )
        t['gift_list'] = l
    else:
        t['gift'] = False
    return JsonResponse(t)

update_info = {'code': 200,
            'version': 1.531,
            'min_version': 1.531,
            'message': u'1、增加“福利”，在“我的”界面下。\n2、增加自动云同步功能，这下你的收藏不会丢失了。\n3、增加@提醒功能，在评论上长按即可@该用户。\n4、修正其他错误',
            'down_link': 'https://d.pujia8.com/apk/com.pujia8.app_1.532.apk'
    }

def check_update(request):
    return JsonResponse(update_info)

def focus(request):
    flatpage = get_object_or_404(FlatPage, url = '/app_focus/')
    date = json.loads(flatpage.content)
    new_games = Games.objects.select_related().exclude(apk_name = None).exclude(apk_name = '').filter(platform = 8, post='1').order_by('-add_time')[:15]
    date["new_games_list"] = games2json(new_games)
    hot_games = Games.objects.select_related().exclude(apk_name = None).exclude(apk_name = '').filter(platform = 8, post='1', hot = '1').order_by('-add_time')[:15]
    date["hot_games_list"] = games2json(hot_games)
    return JsonResponse(date)

def forums_info(request):
    categories = cache.get('categories')
    if not categories:
        categories = Category.objects.all()
        cache.set('categories', categories, 1800)
    t = []
    for category in categories:
        forum_list = []
        tmp = {}
        for forum in category.forum_set.filter(show_in_ui = True):
            type_list = []
            for topictype in forum.topictype_set.all():
                type_list.append({'type_name': topictype.name, 'type_id': topictype.id})
            forum_list.append({'forum_name': forum.name, 'forum_id': forum.id, 'type_list': type_list,
                               'num_topics': forum.num_topics, 'num_posts': forum.num_posts})
        tmp['category_name'] = category.name
        tmp['forum_list'] = forum_list
        t.append(tmp)
    data = {
        'result': t
    }
    return JsonResponse(data)

def get_user_info(user):
    user_profile = user.get_profile()
    if not user_profile.introduce:
        user_profile.introduce = '关注我可获取更多资讯哦'
    try:
        user_avatar_url = gravatar_for_user(user)
    except:
        user_avatar_url = '/static/img/tx.jpg'
    data = {
        'state': 1,
        'version': 1.0,
        'user_info': {
            'user_id': user.pk,
            'user_name': user.username,
            'user_avatar_url': user_avatar_url,
            'user_description': user_profile.introduce,
            'user_pp': user_profile.pp,
            'user_check_in': user_profile.check_in,
            'user_check_in_total': user_profile.check_in_total,
        }
    }
    return data

def users2json(users):
    users_list = []
    for user in users:
        users_list.append(get_user_info(user)['user_info'])
    return users_list

@token_required
def user_info(request):
    if request.method == 'POST':
        data = get_user_info(request.user)
        return JsonResponse(data)
    else:
        return JsonError("Only POST is allowed")

def author(request, user_id):
    since_time = request.GET.get('since_time')
    max_time = request.GET.get('max_time')
    flows = Flow.objects.select_related().filter(user_id = user_id).order_by('-add_time')
    if since_time:
        since_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(since_time)))
        flows = flows.filter(add_time__lt = since_time)
    if max_time:
        max_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(int(max_time)+1)))
        flows = flows.filter(add_time__gt = max_time).order_by('add_time')
    rspd = {}
    rspd['flows_list'] = flows2json(flows[:15])
    user = User.objects.select_related().get(pk = user_id)
    rspd['user_info'] = get_user_info(user)['user_info']
    return JsonResponse(rspd)

@token_required
def post_reply(request):
    if request.method == 'POST':
        topic = get_object_or_404(Topic, id = (request.POST['topic_id']))
        if topic.closed:
            return JsonError(u"帖子已关闭。")
        posted_by = request.user
        poster_ip = request.META['REMOTE_ADDR']
        message = request.POST['content']
        if '@' in message:
            name_list = re.findall('\@([\S]*)', message)
            for name in name_list:
                try:
                    at_user = User.objects.select_related().get(username__exact=name)
                    user_profile = at_user.get_profile()
                    user_profile.notification += 1
                    user_profile.save(update_fields=['notification'])
                except:
                    pass

        if Post.objects.select_related().filter(message=message).exists():
            return JsonError(u"请勿重复提交。")

        p = Post(topic=topic, posted_by=posted_by, poster_ip=poster_ip, message=message)
        p.save()
        date = {"state": 1, 'msg': u'成功发送'}
        return JsonResponse(date)
    else:
        return JsonError("Only POST is allowed")

@token_required
def post_topic(request):
    if request.method == 'POST':
        forum = get_object_or_404(Forum, id = request.POST['forum_id'])
        topic_type = None
        if 'type_id' in request.POST:
            type_id = request.POST['type_id']
            if type_id:
                topic_type = get_object_or_404(TopicType, id = type_id)
        posted_by = request.user
        subject = request.POST['subject']
        if len(subject) < 5:
            return JsonError(u"请认真写清楚主题。")
        poster_ip = request.META['REMOTE_ADDR']
        message = request.POST['content']

        if len(message) < 10:
            return JsonError(u"请勿灌水，内容不得少于10字。")

        if Post.objects.select_related().filter(message=message).exists():
            return JsonError(u"请勿重复提交。")

        topic = Topic(forum=forum, topic_type=topic_type, posted_by=posted_by, subject=subject)
        topic.save()
        post = Post(topic=topic, posted_by=posted_by, poster_ip=poster_ip, message=message, topic_post=True)
        post.save()
        topic.post = post
        topic.save()
        date = {"state": 1, 'msg': u'成功发送'}
        return JsonResponse(date)
    else:
        return JsonError("Only POST is allowed")

@csrf_exempt
def register(request):
    if request.method=="POST":
        username = request.POST["username"]
        if User.objects.filter(username__iexact=username).exists():
            return JsonError(u"此用户名已存在。")
        email = request.POST["email"]
        if User.objects.filter(email__iexact=email).exists():
            return JsonError(u"此邮箱已被注册。")
        password = request.POST["password"]
        url = request.POST['avatar_url'][8:]
        user = User.objects.create_user(username, email, password)
        user.save()

        today = time.strftime("%Y-%m-%d", time.localtime())
        profile = Profile(user=user, avatar=url, today=today)
        profile.save()
        date = {"state": 1,
                "msg": u"注册成功",
                'user_info': get_user_info(user)['user_info']
        }
        return JsonResponse(date)
    else:
        return JsonError("Only POST is allowed")

@csrf_exempt
def sleep(request):
    if request.method == 'POST':
        word = request.POST['w']
        import codecs
        if u'陪我睡' in word:
            voice_dat = codecs.open('/alidata1/pujiahh/weixin/voice0328.json','rb','utf8').read()
            voice_json = json.loads(voice_dat)
            if '#' in word:
                p = re.compile(r'.*#(.*)#.*')
                cv = p.sub(r'\1', word)
                voice_json = [j for j in voice_json if cv in j['title']]
            voice_dic = random.choice(voice_json)
            voice_dic['avatar_url'] = '/static/img/bftx.jpg'
            return JsonResponse(voice_dic)
        elif u'跟你睡' in word:
            voice_dat = codecs.open('/alidata1/pujiahh/weixin/voice_gf.json','rb','utf8').read()
            voice_json = json.loads(voice_dat)
            voice_dic = random.choice(voice_json)
            voice_dic['avatar_url'] = '/static/img/bftx.jpg'
            return JsonResponse(voice_dic)
        else:
            date = {"state": 3}
            return JsonResponse(date)
    else:
        return JsonError("Only POST is allowed")

def gallerys2json(gallerys):
    gallerys_list = []
    for gallery in gallerys:
        t = {}
        t['gallery_id'] = gallery.id
        t['title'] = gallery.title
        t['tags'] = gallery.tags
        t['add_time'] = gallery.add_time.strftime("%Y-%m-%d %H:%M:%S")
        imgs = gallery.imgs.all()
        try:
            t['imgs'] = [get_thumbnailer(img.imagefile).get_thumbnail(options2).url for img in imgs]
        except:
            t['imgs'] = []
        gallerys_list.append(t)
    return gallerys_list

def gallery(request):
    since_id = request.GET.get('since_id')
    max_id = request.GET.get('max_id')
    if since_id:
        since_id = int(since_id)
        gallerys = GalleryApp.objects.select_related().filter(id__lt = since_id).order_by('-id')[:15]
    elif max_id:
        max_id = int(max_id)
        gallerys = GalleryApp.objects.select_related().filter(id__gt = max_id).order_by('id')[:15]
    else:
        gallerys = GalleryApp.objects.select_related().all().order_by('-id')[:15]
    rspd = {}
    rspd['code'] = 200
    rspd['version'] = 0.1
    rspd['data'] = gallerys2json(gallerys)
    return JsonResponse(rspd)

def get_gallerys_tag(request, gallery_tag):
    gallery_tag = Tag.objects.get(name = gallery_tag)
    since_id = request.GET.get('since_id')
    max_id = request.GET.get('max_id')
    if since_id:
        since_id = int(since_id)
        gallerys = TaggedItem.objects.get_by_model(GalleryApp.objects.select_related().filter(id__lt = since_id).order_by('-id'), gallery_tag)[:15]
    elif max_id:
        max_id = int(max_id)
        gallerys = TaggedItem.objects.get_by_model(GalleryApp.objects.select_related().filter(id__gt = max_id).order_by('id'), gallery_tag)[:15]
    else:
        gallerys = TaggedItem.objects.get_by_model(GalleryApp.objects.select_related().all().order_by('-id'), gallery_tag)[:15]
    rspd = {}
    rspd['code'] = 200
    rspd['version'] = 0.1
    rspd['data'] = gallerys2json(gallerys)
    return JsonResponse(rspd)

def make_img_url(x):
    return domain + x

def wdjgames2json(games):
    games_list = []
    for game in games:
        t = {}
        if game.lastFetchTime:
            t['lastModification'] = game.lastFetchTime.strftime("%Y-%m-%d %H:%M:%S")
        else:
            t['lastModification'] = game.add_time.strftime("%Y-%m-%d %H:%M:%S")
        t['detailUrl'] = '%s/library/%d/'%(domain, game.id)
        t['screenshotsUrl'] = map(make_img_url, re.findall('(/static/[\S]*.[jpg|jpeg|png])', game.content))
        t['packageName'] = game.apk_name_wdj[:-4].split('/')[-1]
        t['versionCode'] = game.versionCode
        if 'http' in game.apk_name_wdj:
            t['downloadUrl'] = game.apk_name_wdj
        else:
            t['downloadUrl'] = 'http://apk.pujia8.com/wandoujia/%s'%(game.apk_name_wdj)
        t['versionName'] = game.versionName
        try:
            t['size'] = int(float((re.sub('[a-zA-Z]', '', game.game_size)))*1024)
        except:
            t['size'] = 0
        t['id'] = game.id
        t['categoryName'] = game.get_categoryName_display()
        if game.language == 'cn':
            label = u' 中文版'
        elif game.language == 'jp':
            label = u' 日文版'
        elif game.language == 'en':
            label = u' 英文版'
        else:
            label = ''
        t['title'] = game.title_cn + label
        t['iconPath'] = domain+game.imagefile.url
        t['price'] = 0
        t['description'] = game.introduce
        t['developer'] = game.developer.strip(' ')
        t['changelog'] = game.changelog
        games_list.append(t)
    return games_list

def wandoujia(request):
    rspd = {}
    lastFetchTime = request.GET.get('lastFetchTime')
    currentPage = request.GET.get('currentPage')
    key = request.GET.get('key')
    if key == 'taw1qvxh6w31o8hv':
        games = Games.objects.select_related().exclude(apk_name_wdj = None).exclude(apk_name_wdj = '').filter(platform = 8).order_by('-lastFetchTime')
        totalEntries = games.count()
        if totalEntries%15 == 0:
            totalPages = totalEntries/15
        else:
            totalPages = totalEntries/15 + 1

        if lastFetchTime:
            lastFetchTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(int(lastFetchTime)+1)))
            games = games.filter(add_time__gt = lastFetchTime).order_by('add_time')
        if currentPage:
            currentPage = int(currentPage)
            games = games[(currentPage-1)*15:currentPage*15]
            rspd['currentPage'] = currentPage
            rspd['totalPages'] = totalPages
            rspd['totalEntries'] = totalEntries
        rspd['items'] = {'item': wdjgames2json(games)}
        res = json.dumps(rspd)
        return HttpResponse(res, content_type="application/json; charset=UTF-8")
    else:
        return HttpResponse('error key')

def apps2json(games):
    games_list = []
    for game in games:
        t = {}
        if game.lastFetchTime:
            t['lastModification'] = game.lastFetchTime.strftime("%Y-%m-%d %H:%M:%S")
        else:
            t['lastModification'] = game.add_time.strftime("%Y-%m-%d %H:%M:%S")
        t['detailUrl'] = '%s/library/%d/'%(domain, game.id)
        t['screenshotsUrl'] = map(make_img_url, re.findall('(/static/[\S]*.[jpg|jpeg|png])', game.content))
        t['packageName'] = game.package
        if 'http' in game.apk_name:
            t['downloadUrl'] = game.apk_name
        else:
            t['downloadUrl'] = 'http://apk.pujia8.com/apk/%s'%(game.apk_name)
        try:
            t['size'] = int(float((re.sub('[a-zA-Z]', '', game.game_size)))*1024)
        except:
            t['size'] = 0
        t['id'] = game.id
        t['categoryName'] = game.get_categoryName_display()
        t['title'] = game.title_cn
        t['iconPath'] = domain+game.imagefile.url
        t['price'] = 0
        t['description'] = game.introduce
        games_list.append(t)
    return games_list

def apps(request):
    rspd = {}
    lastFetchTime = request.GET.get('lastFetchTime')
    currentPage = request.GET.get('currentPage')
    key = request.GET.get('key')
    if key == 'tqw9qvxz6w79z8hv':
        games = Games.objects.select_related().exclude(apk_name = None).exclude(apk_name = '').filter(platform = 8, language = 'cn').order_by('-add_time')
        totalEntries = games.count()
        if totalEntries%15 == 0:
            totalPages = totalEntries/15
        else:
            totalPages = totalEntries/15 + 1

        if lastFetchTime:
            lastFetchTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(int(lastFetchTime)+1)))
            games = games.filter(add_time__gt = lastFetchTime).order_by('add_time')
        if currentPage:
            currentPage = int(currentPage)
            games = games[(currentPage-1)*15:currentPage*15]
            rspd['currentPage'] = currentPage
            rspd['totalPages'] = totalPages
            rspd['totalEntries'] = totalEntries
        rspd['items'] = {'item': apps2json(games)}
        res = json.dumps(rspd)
        return HttpResponse(res, content_type="application/json; charset=UTF-8")
    else:
        return HttpResponse('error key')

@cache_page(60 * 30)
def get_emoji(request):
    data = []
    emoji_list = Emoji.objects.select_related().all().order_by('-id')
    for emoji in emoji_list:
        tmp = {'name': emoji.name}
        emoji_img_list = Emoji_img.objects.select_related().filter(emoji = emoji)
        tmp2 = []
        for emoji_img in emoji_img_list:
            tmp2.append({
                'description': emoji_img.description,
                'emoji_url': emoji_img.img.url,
            })
        tmp['emoji_img_list'] = tmp2
        data.append(tmp)
    return JsonResponse(data)


def flow2json(flow, related = False):
    t = {}
    t['flow_id'] = flow.id
    t['title'] = flow.title
    t['channel'] = [v.name for v in flow.channel.all()]
    t['column'] = [v.name for v in flow.column.all()]
    t['tags'] = flow.tags
    video = False
    if Video_info.objects.select_related().filter(flow_id=flow.id).exists():
        video = True
        video_info = Video_info.objects.select_related().get(flow_id=flow.id)
        if flow.show_type == u'1':
            cover = get_thumbnailer(video_info.cover.url[8:]).get_thumbnail(options_large).url
        else:
            cover = get_thumbnailer(video_info.cover.url[8:]).get_thumbnail(options_small).url
        video_arg = {'cid': video_info.cid, 'cover': cover, 'duration': video_info.duration}
        t['video_arg'] = video_arg
    pub_time = flow.add_time.strftime("%Y-%m-%d %H:%M:%S")
    t['pub_time'] = pub_time
    t['pub_mktime'] = int(time.mktime(time.strptime(pub_time, '%Y-%m-%d %H:%M:%S')))
    t['url'] = flow.url
    t['user_info'] = get_user_info(flow.user)['user_info']
    t['show_type'] = flow.show_type

    pics_list = re.findall('/static/[a-zA-z0-9/\.]+[jpg|JPG|jpeg|JPEG|png|PNG]', flow.content)
    if flow.head_img:
        pics_list.append(flow.head_img)

    if pics_list:
        try:
            if not flow.head_img:
                flow.head_img = '/static/pics/ac20007d581324bcd36.jpg'
            if len(pics_list) > 2:
                pics_list = pics_list[:3]
            if flow.show_type == u'0':
                t['pics'] = [get_thumbnailer(flow.head_img[8:]).get_thumbnail(options_small).url]
            elif flow.show_type == u'1':
                t['pics'] = [get_thumbnailer(flow.head_img[8:]).get_thumbnail(options_large).url]
            else:
                t['pics'] = [get_thumbnailer(p[8:]).get_thumbnail(options_small).url for p in pics_list]
        except:
            t['pics'] = []
    else:
        t['pics'] = []
        if not video:
            t['show_type'] = 'n'

    if flow.show_type == '2':
        t['show_type'] = '0'
    if related:
        t['show_type'] = '0'

    if flow.head_img:
        try:
            t['head_img'] = get_thumbnailer(flow.head_img[8:]).get_thumbnail(options_large).url
        except:
            t['head_img'] = '/static/pics/ac20007d581324bcd36.jpg'
    else:
        t['head_img'] = '/static/pics/ac20007d581324bcd36.jpg'
    t['count'] = flow.count
    t['comment_num'] = flow.comment
    return t

def flows2json(flows, related = False):
    flows_list = []
    for flow in flows:
        flows_list.append(flow2json(flow, related))
    return flows_list


def schema(request):
    rspd = {}
    schema = []
    channels = Channel.objects.select_related().all()
    for channel in channels:
        t = {}
        t['name'] = channel.name
        # t['icon'] = channel.icon.url
        t['color'] = channel.color
        columns = Column.objects.select_related().filter(channel__name = channel.name, display = True)
        t['column_list'] = [c.name for c in columns]
        schema.append(t)
    rspd['schema'] = schema
    rspd['code'] = 200
    return JsonResponse(rspd)


@csrf_exempt
def commend(request):
    if request.method=="POST":
        flows = Flow.objects.select_related().filter(post = True, hot = True, sticky = False).distinct().order_by('-add_time')
        if 'column_list' in request.POST:
            flows = flows.filter(column__name__in = json.loads(request.POST['column_list']))
        if 'since_time' in request.POST:
            since_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(request.POST['since_time'])))
            flows = flows.filter(add_time__lt = since_time)
        if 'max_time' in request.POST:
            max_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(int(request.POST['max_time'])+1)))
            flows = flows.filter(add_time__gt = max_time).order_by('add_time')
        rspd = {
            'code': 200,
            'flows_list': flows2json(flows[:15]),
        }
        return JsonResponse(rspd)
    else:
        return JsonError("hello")


def flow_list(request, column_name):
    since_time = request.GET.get('since_time')
    max_time = request.GET.get('max_time')
    flows = Flow.objects.select_related().filter(column__name = column_name, post = True, sticky = False).distinct().order_by('-add_time')
    if since_time:
        since_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(since_time)))
        flows = flows.filter(add_time__lt = since_time)
    if max_time:
        max_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(int(max_time)+1)))
        flows = flows.filter(add_time__gt = max_time).order_by('add_time')
    rspd = {
        'code': 200,
        'flows_list': flows2json(flows[:15]),
    }
    return JsonResponse(rspd)

def flows_sticky_list(request, column_name = None):
    flows_sticky = Flow.objects.select_related().filter(sticky = True, post = True).order_by('-add_time')
    if column_name:
        flows_sticky = flows_sticky.filter(column__name = column_name)
    if flows_sticky:
        flows_sticky = flows_sticky[:1]
    rspd = {
        'code': 200,
        'flows_sticky_list': flows2json(flows_sticky),
    }
    return JsonResponse(rspd)

def flowinfo(request, fid):
    flow = Flow.objects.select_related().get(id = fid)
    flow.count += 1
    flow.save(update_fields = ['count'])
    rspd = flow2json(flow)
    rspd['content'] = flow.content
    flows = TaggedItem.objects.get_union_by_model(Flow, flow.tags.split(' ')).filter(post = True).exclude(id = fid).order_by('-add_time')
    rspd['flow_related_list'] = flows2json(flows[:3], True)
    rspd['code'] = 200
    return JsonResponse(rspd)


def flow_list_tag(request, tag):
    since_time = request.GET.get('since_time')
    max_time = request.GET.get('max_time')
    tag = Tag.objects.select_related().get(name = tag)
    flows = TaggedItem.objects.get_by_model(Flow, tag).distinct().order_by('-add_time')
    if since_time:
        since_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(since_time)))
        flows = flows.filter(add_time__lt = since_time)
    if max_time:
        max_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(int(max_time)+1)))
        flows = flows.filter(add_time__gt = max_time).order_by('add_time')
    rspd = {'code': 200,
            'flows_list': flows2json(flows[:15])
    }
    return JsonResponse(rspd)

def flow_list_date(request, date):
    since_time = request.GET.get('since_time')
    max_time = request.GET.get('max_time')
    flows = Flow.objects.select_related().filter(add_time__contains = date, post = True).distinct().order_by('-add_time')
    if since_time:
        since_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(since_time)))
        flows = flows.filter(add_time__lt = since_time)
    if max_time:
        max_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(int(max_time)+1)))
        flows = flows.filter(add_time__gt = max_time).order_by('add_time')
    rspd = {'code': 200,
            'flows_list': flows2json(flows[:15])
    }
    return JsonResponse(rspd)


def flow_related_list(request, flow_id):
    since_time = request.GET.get('since_time')
    max_time = request.GET.get('max_time')
    flow = Flow.objects.select_related().get(id = flow_id)
    flows = TaggedItem.objects.get_union_by_model(Flow, flow.tags.split(' ')).distinct().filter(post = True).exclude(id = flow_id).order_by('-add_time')
    if since_time:
        since_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(since_time)))
        flows = flows.filter(add_time__lt = since_time)
    if max_time:
        max_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(int(max_time)+1)))
        flows = flows.filter(add_time__gt = max_time).order_by('add_time')
    rspd = {}
    rspd['code'] = 200
    rspd['flows_list'] = flows2json(flows[:15])
    return JsonResponse(rspd)


@token_required
def subs(request, user_id):
    if request.method=="POST":
        rspd = {}
        rspd['code'] = 200
        desc_user = User.objects.select_related().get(pk = user_id)
        if Subscription.objects.select_related().filter(src_user = request.user, desc_user = desc_user).exists():
            return JsonError(u'你已经订阅过此用户')
        else:
            s = Subscription(src_user = request.user, desc_user = desc_user)
            s.save()
            rspd['msg'] = u'成功订阅用户'
            return JsonResponse(rspd)
    else:
        return JsonError("hello")

@token_required
def unsubs(request, user_id):
    if request.method=="POST":
        rspd = {}
        rspd['code'] = 200
        subs = Subscription.objects.select_related().get(src_user = request.user, desc_user_id = user_id)
        subs.delete()
        rspd['msg'] = u'已取消订阅此用户'
        return JsonResponse(rspd)
    else:
        return JsonError("hello")

@token_required
def subs_tag(request, tag_name):
    if request.method=="POST":
        rspd = {}
        rspd['code'] = 200
        tag = Tag.objects.select_related().get(name = tag_name)
        if Subscription_Tag.objects.select_related().filter(user = request.user, tag = tag).exists():
            return JsonError(u'你已经订阅过此标签')
        else:
            s = Subscription_Tag(user = request.user, tag = tag)
            s.save()
            rspd['msg'] = u'成功订阅标签'
            return JsonResponse(rspd)
    else:
        return JsonError("hello")

@token_required
def unsubs_tag(request, tag_name):
    if request.method=="POST":
        rspd = {}
        rspd['code'] = 200
        tag = Tag.objects.select_related().get(name = tag_name)
        subs = Subscription_Tag.objects.select_related().get(user = request.user, tag = tag)
        subs.delete()
        rspd['msg'] = u'已取消订阅此标签'
        return JsonResponse(rspd)
    else:
        return JsonError("hello")

@token_required
def subs_list(request):
    if request.method=="POST":
        rspd = {}
        rspd['code'] = 200
        subs_list = Subscription.objects.select_related().filter(src_user = request.user).order_by('-id')
        # if 'since_id' in request.POST:
        #     since_id = request.POST['since_id']
        #     subs_list = subs_list.filter(id__lt = since_id)
        # if 'max_id' in request.POST:
        #     max_id = request.POST['max_id']
        #     subs_list = subs_list.filter(id__gt = max_id).order_by('id')
        user_info_list = []
        for subs in subs_list:
            user_info_list.append(user_info(subs.desc_user))
        rspd['subs_list'] = user_info_list
        return JsonResponse(rspd)
    else:
        return JsonError("hello")

@token_required
def coll(request, target_id):
    if request.method=="POST":
        target = request.POST['target']
        if target == 'new':
            flow = Flow.objects.select_related().get(pk = target_id)
            if Collection.objects.select_related().filter(user = request.user, flow = flow).exists():
                return JsonError(u'你已经收藏过了')
            else:
                c = Collection(user = request.user, flow = flow)
                c.save()

        if target == 'game':
            game = Games.objects.select_related().get(pk = target_id)
            if GameCollection.objects.select_related().filter(user = request.user, game = game).exists():
                return JsonError(u'你已经收藏过了')
            else:
                c = GameCollection(user = request.user, game = game)
                c.save()

        if target == 'topic':
            return JsonError(u'你已经收藏过了')

        rspd = {'msg': u'收藏成功'}
        return JsonResponse(rspd)
    else:
        return JsonError("hello")

@token_required
def uncoll(request, target_id):
    if request.method=="POST":
        rspd = {}
        rspd['code'] = 200
        coll = Collection.objects.select_related().get(user = request.user, flow_id = flow_id)
        coll.delete()
        rspd['msg'] = u'已取消收藏'
        return JsonResponse(rspd)
    else:
        return JsonError("hello")

@token_required
def coll_list(request):
    if request.method=="POST":
        rspd = {}
        rspd['code'] = 200
        coll_list = Collection.objects.select_related().filter(user = request.user).order_by('-id')
        # if 'since_id' in request.POST:
        #     since_id = request.POST['since_id']
        #     coll_list = coll_list.filter(id__lt = since_id).order_by('-id')
        # if 'max_id' in request.POST:
        #     max_id = request.POST['max_id']
        #     coll_list = coll_list.filter(id__gt = max_id).order_by('id')
        flows = [coll.flow for coll in coll_list]
        rspd['flows_list'] = flows2json(flows)
        return JsonResponse(rspd)
    else:
        return JsonError("hello")

@token_required
def change_avatar(request):
    if request.method=="POST":
        url = request.POST['avatar_url'][8:]
        profile = request.user.get_profile()
        profile.avatar = url
        profile.save()
        date = {
            "msg": u"更改成功",
        }
        return JsonResponse(date)
    else:
        return JsonError("hello")

@token_required
def sync(request):
    if request.method=="POST":
        dat = request.POST['all_user']
        profile = request.user.get_profile()
        profile.app_sync = b64encode(dat)
        profile.save(update_fields=['app_sync'])
        rspd = {
            'msg': u'同步完毕',
            'check_update': update_info,
            'notification_num': profile.notification,
        }
        return JsonResponse(rspd)
    else:
        return JsonError("hello")

@token_required
def get_notification_num(request):
    if request.method == "POST":
        profile = request.user.get_profile()
        rspd = {
            'notification_num': profile.notification,
        }
        return JsonResponse(rspd)
    else:
        return JsonError("hello")

def posts2json(posts):
    comment_list = []
    for post in posts:
        t = {}
        t['comment_id'] = post.id
        pub_time = post.created_on.strftime("%Y-%m-%d %H:%M:%S")
        t['pub_time'] = pub_time
        t['pub_mktime'] = int(time.mktime(time.strptime(pub_time,'%Y-%m-%d %H:%M:%S')))
        t['content'] = post.message
        t['user_info'] = get_user_info(post.posted_by)['user_info']
        t['parent'] = {
            'parent_id': post.topic_id,
            'title': post.topic.subject,
        }
        comment_list.append(t)
    return comment_list

@token_required
def get_notification_list(request, type):
    if request.method == "POST":
        user = request.user
        user_profile = user.get_profile()
        user_profile.notification = 0
        user_profile.save(update_fields=['notification'])
        since_time = max_time = False
        if 'since_time' in request.POST:
            since_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(request.POST['since_time'])))
        if 'max_time' in request.POST:
            max_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(int(request.POST['max_time'])+1)))
        if type == 'topic':
            comments = Post.objects.filter(Q(message__contains='@%s ' % user.username) | Q(
                message__contains='@%s\n' % user.username)).order_by('-created_on').select_related()
            if since_time:
                comments = comments.filter(created_on__lt = since_time)
            if max_time:
                comments = comments.filter(created_on__gt = max_time)
            rspd = {'comments': posts2json(comments[:15])}
            return JsonResponse(rspd)

        if type == 'game':
            comments = PujiaComment.objects.filter(content__contains='@%s' % user.username,
                                                        target__contains='library').order_by('-date').select_related()
            if since_time:
                comments = comments.filter(date__lt = since_time)
            if max_time:
                comments = comments.filter(date__gt = max_time).order_by('date')
            rspd = {'comments': comments2json(comments[:15], 'game')}
            return JsonResponse(rspd)

        if type == 'new':
            comments = PujiaComment.objects.filter(content__contains='@%s' % user.username,
                                                       target__contains='news').order_by('-date').select_related()
            if since_time:
                comments = comments.filter(date__lt = since_time)
            if max_time:
                comments = comments.filter(date__gt = max_time).order_by('date')
            rspd = {'comments': comments2json(comments[:15], 'new')}
            return JsonResponse(rspd)
    else:
        return JsonError("hello")

@token_required
def post_comment(request):
    if request.method == 'POST':
        user = request.user
        target = ''
        if 'game_id' in request.POST:
            target = '/library/%s/'%(request.POST['game_id'])
        if 'flow_id' in request.POST:
            target = '/news/%s/' % (request.POST['flow_id'])
        content = request.POST['content']
        if '@' in content:
            name_list = re.findall('\@([\S]*)', content)
            for name in name_list:
                try:
                    at_user = User.objects.select_related().get(username__exact=name)
                    user_profile = at_user.get_profile()
                    user_profile.notification += 1
                    user_profile.save(update_fields=['notification'])
                except:
                    pass

        if len(content) < 10:
            return JsonError(u"请勿灌水，内容不得少于10字。")

        if PujiaComment.objects.select_related().filter(content=content).exists():
            return JsonError(u"请勿重复提交。")

        c = PujiaComment(name=user, target=target, content=content)
        c.save()
        rspd = {"state": 1, 'msg': '成功发送'}
        return JsonResponse(rspd)
    else:
        return JsonError("Only POST is allowed")


def comments2json(comments, type = None):
    comment_list = []
    for comment in comments:
        try:
            t = {}
            t['comment_id'] = comment.id
            pub_time = comment.date.strftime("%Y-%m-%d %H:%M:%S")
            t['pub_time'] = pub_time
            t['pub_mktime'] = int(time.mktime(time.strptime(pub_time,'%Y-%m-%d %H:%M:%S')))
            t['content'] = comment.content
            t['hot'] = comment.hot
            t['positive'] = comment.positive
            t['user_info'] = get_user_info(comment.name)['user_info']
            p = True
            if type == 'game':
                game_id = int(comment.target.split('/')[2])
                game = Games.objects.select_related().get(id = game_id)
                t['parent'] = {
                    'parent_id': game_id,
                    'title': game.title_cn,
                    'package': game.package,
                    'versionName': game.platform.all()[0].platform.upper(),
                    'emu_game_code': game.emu_game_code,
                }
                if not game.package or game.emu_game_code:
                    p = False

            if type == 'new':
                new_id = int(comment.target.split('/')[2])
                flow = Flow.objects.select_related().get(id = new_id)
                video_arg = {}
                if Video_info.objects.select_related().filter(flow_id=flow.id).exists():
                    video_info = Video_info.objects.select_related().get(flow_id=flow.id)
                    if flow.show_type == u'1':
                        cover = get_thumbnailer(video_info.cover.url[8:]).get_thumbnail(options_large).url
                    else:
                        cover = get_thumbnailer(video_info.cover.url[8:]).get_thumbnail(options_small).url
                    video_arg = {'cid': video_info.cid, 'cover': cover, 'duration': video_info.duration}

                d = {
                    'parent_id': new_id,
                    'title': flow.title,
                }
                if video_arg:
                    d['video_arg'] = video_arg
                t['parent'] = d
            if p:
                comment_list.append(t)
        except:
            pass
    return comment_list

def comment_list(request):
    since_id = request.GET.get('since_id')
    max_id = request.GET.get('max_id')
    game_id = request.GET.get('game_id')
    new_id = request.GET.get('new_id')
    if game_id:
        comments = PujiaComment.objects.select_related().filter(target = '/library/%s/'%game_id).order_by('-date')
    if new_id:
        comments = PujiaComment.objects.select_related().filter(target='/news/%s/'%new_id).order_by('-date')
    num = comments.count()
    if since_id:
        since_id = int(since_id)
        comments = comments.filter(id__lt = since_id)
    if max_id:
        max_id = int(max_id)
        comments = comments.filter(id__gt = max_id).order_by('date')
    rspd = {
        'code': 200,
        'num': num,
        'comment_list': comments2json(comments[:15])
    }
    return JsonResponse(rspd)

@token_required
def comment_positive(request, comment_id):
    comment = get_object_or_404(PujiaComment, id=comment_id)
    if comment.name == request.user:
        return JsonError(u'不能赞自己的评论。')
    if CommentPositive.objects.select_related().filter(user=request.user, comment=comment).exists():
        return JsonError(u'你已赞过此条评论。')
    comment.positive += 1
    comment.save(update_fields=['positive'])
    cp = CommentPositive(user=request.user, comment=comment)
    cp.save()
    rspd = {
        'msg': '点赞成功',
        'positive': comment.positive
    }
    return JsonResponse(rspd)

#old
def get_game_comments(request, package):
    game = get_object_or_404(Games, package = package)
    target = '/library/%d/'%(game.id)

    since_id = request.GET.get('since_id')
    max_id = request.GET.get('max_id')
    if since_id:
        since_id = int(since_id)
        comments = PujiaComment.objects.select_related().filter(id__lt = since_id, target = target).order_by('-date')[:15]
    elif max_id:
        max_id = int(max_id)
        comments = PujiaComment.objects.select_related().filter(id__gt = max_id, target = target).order_by('date')[:15]
    else:
        comments = PujiaComment.objects.select_related().filter(target = target).order_by('-date')[:15]

    comments_list = []
    for comment in comments:
        p = {}
        p['comment_id'] = comment.id
        p['user_name'] = comment.name.username
        p['user_gravatar'] = gravatar_for_user(comment.name)
        p['created_on'] = str(comment.date)
        p['content'] = comment.content
        comments_list.append(p)

    rspd = {'code': 200, 'version': 0.1, 'comments_list': comments_list}
    return JsonResponse(rspd)


def game_search(request):
    word = request.GET.get('w')
    if word:
        since_id = request.GET.get('since_id')
        max_id = request.GET.get('max_id')
        since_time = request.GET.get('since_time')
        max_time = request.GET.get('max_time')
        games = Games.objects.select_related().exclude(apk_name = None).exclude(apk_name = '').filter(platform = 8, title_cn__icontains = word, post='1').order_by('-add_time')
        if since_id:
            since_id = int(since_id)
            games = games.filter(id__lt = since_id)
        if max_id:
            max_id = int(max_id)
            games = games.filter(id__gt = max_id).order_by('add_time')
        if since_time:
            since_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(since_time)))
            games = games.filter(add_time__lt=since_time)
        if max_time:
            max_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(int(max_time) + 1)))
            games = games.filter(add_time__gt=max_time).order_by('add_time')
        rspd = {'code': 200, 'version': 0.1, 'games_list': games2json(games[:15])}
        return JsonResponse(rspd)
    else:
        return JsonError('请先输入搜索关键词')

def topic_search(request):
    since_id = request.GET.get('since_id')
    max_id = request.GET.get('max_id')
    since_time = request.GET.get('since_time')
    max_time = request.GET.get('max_time')
    word = request.GET.get('w')
    if word:
        topics = Topic.objects.select_related().filter(subject__icontains= word).order_by('-created_on')
        if since_id:
            since_id = int(since_id)
            topics = topics.filter(id__lt = since_id)
        if max_id:
            max_id = int(max_id)
            topics = topics.filter(id__gt = max_id).order_by('created_on')
        if since_time:
            since_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(since_time)))
            topics = topics.filter(last_reply_on__lt=since_time).order_by('-last_reply_on')
        if max_time:
            max_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(int(max_time) + 1)))
            topics = topics.filter(last_reply_on__gt=max_time).order_by('last_reply_on')

        rspd = {'topics_list': topics2json(topics[:15])}
        return JsonResponse(rspd)
    else:
        return JsonError('请先输入搜索关键词')

def flow_search(request):
    since_id = request.GET.get('since_id')
    max_id = request.GET.get('max_id')
    since_time = request.GET.get('since_time')
    max_time = request.GET.get('max_time')
    word = request.GET.get('w')
    if word:
        flows = Flow.objects.select_related().filter(title__icontains= word, post = True).distinct().order_by('-add_time')
        if since_id:
            since_id = int(since_id)
            flows = flows.filter(id__lt = since_id)
        if max_id:
            max_id = int(max_id)
            flows = flows.filter(id__gt = max_id).order_by('add_time')
        if since_time:
            since_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(since_time)))
            flows = flows.filter(add_time__lt=since_time)
        if max_time:
            max_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(int(max_time) + 1)))
            flows = flows.filter(add_time__gt=max_time).order_by('add_time')
        rspd = {'flows_list': flows2json(flows[:15])}
        return JsonResponse(rspd)
    else:
        return JsonError('请先输入搜索关键词')

def bili_api_url(request, flow_id):
    flow = Flow.objects.select_related().get(id = flow_id)
    if 'www.bilibili.com' in flow.url:
        aid = flow.url.split('/av')[1][:-1]
        rspd = {
            'url': 'http://api.bilibili.com/playurl?aid=%s&page=1&platform=html5&quality=1&vtype=mp4&type=json&token=1'%aid
        }
        return JsonResponse(rspd)
    else:
        return JsonError(u'not video')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
    'Referer': 'http://www.baidu.com/',
    'X-Forwarded-For': '93.46.8.89',
}

def get_internet_dat(url, headers = headers):
    req = urllib2.Request(url, None, headers)
    dat = urllib2.urlopen(req).read()
    return dat

def save_img(img, ext = '.jpg', headers = headers):
    name = '/static/uploads/' + time.strftime('%Y%m%d%H%M%S') + '_%d'% random.randint(0, 100) + ext
    pic_dat = get_internet_dat(img, headers)
    fn = os.path.dirname(__file__)[:-4] + name
    dst = open(fn, 'wb')
    dst.write(pic_dat)
    return name

def content_save_img(content, headers = headers):
    imgs = content.find_all('img')
    content = unicode(content)
    for img in imgs:
        try:
            img = img.get('src')
            name = '/static/pics/' + time.strftime('%Y%m%d%H%M%S') + '_%d'% random.randint(0, 100) + '.jpg'
            pic_dat = get_internet_dat(img, headers)
            fn = os.path.dirname(__file__)[:-5] + name
            dst = open(fn, 'wb')
            dst.write(pic_dat)
            content = content.replace(img, name)
        except:
            continue
    return content

def fix_text(text):
    text = text.replace(u'。', u'。\n')
    text = text.replace(u'！', u'！\n')
    return text

def spider_wdj(request, package):
    if not Games.objects.select_related().filter(package = package).exists():
        url = 'http://www.wandoujia.com/apps/%s'%package
        content = get_internet_dat(url)
        content = BeautifulSoup(content, 'html.parser')
        title_cn = content.find('span', class_='title').string
        app_icon = content.find('div', class_='app-icon').find('img').get('src')
        imagefile = save_img(app_icon, '.png')[8:]
        desc = content.find('div', class_='desc-info').find('div')

        game_content = unicode(desc).replace('<div ', '<p ').replace('</div>', '</p>')
        imgs_list = content.find('div', class_='view-box').find('div').find_all('img')
        for img in imgs_list:
            game_content += '<img src = "%s" alt = "%s">'%(save_img(img.get('src')), title_cn)

        file_size_HTML = content.find('meta', itemprop='fileSize').parent
        file_size_HTML.find('meta').decompose()
        for file_size in file_size_HTML.stripped_strings:
            game_size = file_size
        tags_list = content.find('div', class_='side-tags').find_all('div', class_='tag-box')
        tags = ' '.join([tag.find('a').string.strip(' \n') for tag in tags_list])

        publish_time = time.strftime("%Y-%m-%d", time.localtime())
        game = Games(title_cn = title_cn, title_src = title_cn, publish_time = publish_time, tags = tags,
                     game_size = game_size, content = game_content, introduce = fix_text(desc.text), package = package,
                     apk_name = url + '/download', imagefile = imagefile)
        game.save()
        p = Platform.objects.select_related().get(platform = u'Android')
        game.platform.add(p)
        return HttpResponse('spider ok')
    else:
        return HttpResponse('already get')

