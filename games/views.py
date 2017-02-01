# -*- coding:utf-8 -*-

from django.shortcuts import render_to_response, render, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from models import Games, Platform, QiuHanHua, GameScore
from forms import GameForm, GameOrderForm, GameStateForm, GameLanguageForm
from django.views.generic import CreateView
from django.core.urlresolvers import reverse

from tagging.models import Tag, TaggedItem
import json, time

def games_list(request):
    ob = request.GET.get('games_order_by')
    orderform = GameOrderForm(request.GET)
    if not ob:
        if 'games_order_by' in request.COOKIES:
            ob = request.COOKIES["games_order_by"]
        else:
            ob = '-publish_time'
        orderform = GameOrderForm(request.COOKIES)

    state = request.GET.get('games_state')
    stateform = GameStateForm(request.GET)
    if not state:
        if 'games_state' in request.COOKIES:
            state = request.COOKIES["games_state"]
        else:
            state = '1'
        stateform = GameStateForm(request.COOKIES)

    language = request.GET.get('game_language')
    languageform = GameLanguageForm(request.GET)
    if not language:
        if 'game_language' in request.COOKIES:
            language = request.COOKIES["game_language"]
        else:
            language = 'all'
        languageform = GameLanguageForm(request.COOKIES)

    if language == 'all':
        games = Games.objects.select_related().filter(post='1', state=state).order_by(ob, '-id')
    else:
        games = Games.objects.select_related().filter(post='1', state=state, language=language).order_by(ob, '-id')
    return render(request, 'games/games_list.html',{'games': games, \
        'orderform': orderform, 'languageform': languageform, 'stateform': stateform})

def games_by_time(request):
    st = request.GET.get('st')
    et = request.GET.get('et')
    games = Games.objects.select_related().filter(publish_time__gte = st, publish_time__lte = et, post='1', state='1').order_by('-publish_time')
    ndsgames = games.filter(platform = 1)
    pspgames = games.filter(platform = 2)
    wiigames = games.filter(platform = 3)
    ps2games = games.filter(platform = 4)
    gbagames = games.filter(platform = 5)
    iosgames = games.filter(platform = 6)
    pcgames = games.filter(platform = 7)
    androidgames = games.filter(platform = 8)
    ps3games = games.filter(platform = 9)
    etcgames = games.filter(platform = 12)
    return render_to_response('games/games_by_time.html',{'games': games, \
                                                    'ndsgames': ndsgames, 'pspgames': pspgames, \
                                                    'wiigames': wiigames, 'ps2games': ps2games, \
                                                    'gbagames': gbagames, 'iosgames': iosgames, \
                                                    'pcgames': pcgames, 'androidgames': androidgames, \
                                                    'ps3games': ps3games, 'etcgames': etcgames, 'st': st, 'et': et}, \
        context_instance=RequestContext(request))

def category(request, cate):
    ob = request.GET.get('games_order_by')
    orderform = GameOrderForm(request.GET)
    if not ob:
        if 'games_order_by' in request.COOKIES:
            ob = request.COOKIES["games_order_by"]
        else:
            ob = '-publish_time'
        orderform = GameOrderForm(request.COOKIES)

    state = request.GET.get('games_state')
    stateform = GameStateForm(request.GET)
    if not state:
        if 'games_state' in request.COOKIES:
            state = request.COOKIES["games_state"]
        else:
            state = '1'
        stateform = GameStateForm(request.COOKIES)

    language = request.GET.get('game_language')
    languageform = GameLanguageForm(request.GET)
    if not language:
        if 'game_language' in request.COOKIES:
            language = request.COOKIES["game_language"]
        else:
            language = 'all'
        languageform = GameLanguageForm(request.COOKIES)

    cate = cate.upper()
    pid = Platform.objects.get(platform = cate).id
    if language == 'all':
        games = Games.objects.select_related().filter(platform = pid, post='1', state=state).order_by(ob, '-id')
    else:
        games = Games.objects.select_related().filter(platform = pid, post='1', state=state, language=language).order_by(ob, '-id')
    return render_to_response('games/games_category.html',{'games': games, 'cate': cate, \
        'orderform': orderform, 'stateform': stateform, 'languageform': languageform},
        context_instance=RequestContext(request))

def detail(request, gid):
    show = request.GET.get('show', '')
    game = Games.objects.select_related().get(pk = gid)
    game.count += 1
    game.save()

    tags = Tag.objects.get_for_object(game)

    request_user = request.user
    perm_edit_article = False
    if request_user == game.name or request_user.has_perm('games.change_games'):
        perm_edit_article = True

    if show == 'mobile':
        return render_to_response('games/games_detail_mobile.html', {'game': game}, context_instance=RequestContext(request))
    else:
        return render_to_response('games/games_detail.html', {'game': game, 'perm_edit_article': perm_edit_article, 'tags': tags},
        context_instance=RequestContext(request))

def detail_mobile(request, package):
    if Games.objects.select_related().filter(package = package).exists():
        game = Games.objects.select_related().get(package = package)
        return HttpResponseRedirect('/library/%s/?show=mobile' % game.id)
    else:
        return HttpResponseRedirect('/?utm_source=pjgame')

class SubmitGame(CreateView):
    model = Games
    form_class = GameForm
    template_name = "games/submit_game.html"
    success_view_name = "games_list"
    success_url = "/library/?games_order_by=-add_time"

    def get_form_kwargs(self):
        kwargs = super(SubmitGame, self).get_form_kwargs()
        kwargs['instance'] = Games()
        if self.request.user.is_authenticated():
            kwargs['instance'].name = self.request.user
        return kwargs

    def form_valid(self, form):
        if self.request.user.is_authenticated():
            if self.request.user.get_profile().check_in_total >= 0:
                response = super(SubmitGame, self).form_valid(form)
                return response
            else:
                return HttpResponse('error')
        else:
            return HttpResponse('error')

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        else:
            return reverse(self.success_view_name)

def game_edit(request, gid):
    game = Games.objects.select_related().get(pk=gid)

    perm_edit_game = False
    if request.user == game.name or request.user.has_perm('games.change_games'):
        perm_edit_game = True

    form = GameForm(instance = game)

    if request.method == 'POST':
        game.title_cn = request.POST['title_cn']
        game.title_src = request.POST['title_src']
        game.platform = request.POST.getlist('platform')
        game.language = request.POST['language']
        try:
            game.imagefile = request.FILES['imagefile']
        except :
            pass
        game.team = request.POST['team']
        game.level = request.POST['level']
        if request.POST['publish_time']:
            game.publish_time = request.POST['publish_time']
        game.game_size = request.POST['game_size']
        game.tags = request.POST['tags']
        game.publish_url = request.POST['publish_url']
        game.download_link = request.POST['download_link']
        game.content = request.POST['content']
        game.state = request.POST['state']
        if request.POST['review_id']:
            game.review_id = int(request.POST['review_id'])
        else:
            game.review_id = None
        if request.POST['gospel_id']:
            game.gospel_id = int(request.POST['gospel_id'])
        else:
            game.gospel_id = None
        game.save()
        return HttpResponseRedirect('/library/%s/'%gid)
    return render_to_response("games/game_edit.html",{'form': form, 'perm_edit_game': perm_edit_game},\
        context_instance=RequestContext(request))

def games_by_tag(request, platform, game_tag):
    ob = request.GET.get('games_order_by')
    orderform = GameOrderForm(request.GET)
    if not ob:
        if 'games_order_by' in request.COOKIES:
            ob = request.COOKIES["games_order_by"]
        else:
            ob = '-publish_time'
        orderform = GameOrderForm(request.COOKIES)

    language = request.GET.get('game_language')
    languageform = GameLanguageForm(request.GET)
    if not language:
        if 'game_language' in request.COOKIES:
            language = request.COOKIES["game_language"]
        else:
            language = 'all'
        languageform = GameLanguageForm(request.COOKIES)

    if language == 'all':
        games = Games.objects.select_related().filter(post='1', state='1').order_by(ob, '-id')
    else:
        games = Games.objects.select_related().filter(language=language, post='1', state='1').order_by(ob, '-id')

    game_tag = Tag.objects.get(name = game_tag)
    platform = platform.upper()
    if platform != 'ALL':
        pid = Platform.objects.get(platform = platform).id
        games = TaggedItem.objects.get_by_model(games.filter(platform = pid), game_tag)
    else:
        platform = u'全平台'
        games = TaggedItem.objects.get_by_model(games, game_tag)
    return render(request, 'games/games_by_tag.html', {'games': games, 'game_tag': game_tag, \
        'orderform': orderform, 'platform': platform, 'languageform': languageform})

def qiuhanhua(request, game_id):
    rspd = {}
    request_user = request.user
    if not request_user.is_authenticated():
        rspd['msg'] = u'求汉化前请先登录！'
        res = json.dumps(rspd)
        return HttpResponse(res)
    game = get_object_or_404(Games, id = game_id)
    qhh_date = time.strftime("%Y-%m-%d", time.localtime())
    qiuhanhua_user = QiuHanHua.objects.filter(game = game, user = request_user, qhh_date = qhh_date).select_related()
    if qiuhanhua_user:
        rspd['msg'] = u'你今天已经求过了，请明天再来，或者推荐好友来求汉化吧！'
        res = json.dumps(rspd)
        return HttpResponse(res)
    else:
        qiuhanhua = QiuHanHua(game = game, user = request_user, qhh_date = qhh_date)
        qiuhanhua.save()
        game.qiuhanhua_num += 1
        game.week_qiuhanhua_num += 1
        game.save(update_fields = ['qiuhanhua_num', 'week_qiuhanhua_num'])
        up = request_user.get_profile()
        if up.pp < 5:
            rspd['msg'] = u'你的PP不足'
            res = json.dumps(rspd)
            return HttpResponse(res)
        up.pp -= 5
        up.save(update_fields=['pp'])
        rspd['msg'] = u'请求已发送，耗费5PP\n据说达到500就会汉化哦'
        res = json.dumps(rspd)
        return HttpResponse(res)

def gamescore(request, game_id):
    rspd = {}
    request_user = request.user

    game = get_object_or_404(Games, id = game_id)
    if game.name == request_user:
        rspd['msg'] = u'不能宠幸自己！'
        res = json.dumps(rspd)
        return HttpResponse(res)

    score_user = GameScore.objects.filter(game = game, user = request_user).select_related()
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

    score = GameScore(game = game, pp = pp, user = request_user)
    score.save()

    user_profile = game.name.get_profile()
    user_profile.pp += pp
    user_profile.save()

    if not request_user.has_perm('forum.delete_post'):
        request_user_profile.pp -= abs(pp)
    request_user_profile.save()

    rspd['msg'] = u'宠幸成功！'
    res = json.dumps(rspd)
    return HttpResponse(res)

def wandoujia(request):
    games = Games.objects.select_related().exclude(apk_name_wdj = None).exclude(apk_name_wdj = '').filter(platform = 8).order_by('-lastFetchTime')
    return render(request, 'games/games_list_wdj.html',{'games': games})
