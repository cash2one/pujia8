# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import RequestContext, Template
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils.encoding import smart_str, smart_unicode

import urllib2, json
import time, hashlib
from games.models import Games
from forum.models import Topic

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
TOKEN = "79faf82271944fe38c4f1d99be71bc9c"

@csrf_exempt
def handleRequest(request):
    if request.method == 'GET':
        response = HttpResponse(checkSignature(request),content_type="text/plain")
        return response
    elif request.method == 'POST':
        response = HttpResponse(responseMsg(request),content_type="application/xml")
        return response
    else:
        return None

@csrf_exempt
def handleRequestTest(request):
    if request.method == 'GET':
        response = HttpResponse(checkSignature(request),content_type="text/plain")
        return response
    elif request.method == 'POST':
        response = HttpResponse(responseMsgTest(request),content_type="application/xml")
        return response
    else:
        return None

def checkSignature(request):
    global TOKEN
    signature = request.GET.get("signature", None)
    timestamp = request.GET.get("timestamp", None)
    nonce = request.GET.get("nonce", None)
    echoStr = request.GET.get("echostr",None)

    token = TOKEN
    tmpList = [token,timestamp,nonce]
    tmpList.sort()
    tmpstr = "%s%s%s" % tuple(tmpList)
    tmpstr = hashlib.sha1(tmpstr).hexdigest()
    if tmpstr == signature:
        return echoStr
    else:
        return None

def responseMsgTest(request):
    tips = u'①回复“最新汉化”查询最新发布的汉化游戏。\n②回复游戏名称（如：弹丸论破）查询此游戏的相关汉化资讯和下载。\n③回复“陪我睡”可进入淑女模式。\n④回复“跟你睡”可进入绅士模式。'
    from BeautifulSoup import BeautifulSoup
    soup = BeautifulSoup(request.raw_post_data)
    if soup.msgtype.text == 'text':
        word = soup.content.text
        if u'陪我睡' in word:
            import codecs, json, random, re
            voice_dat = codecs.open('/alidata1/pujiahh/weixin/voice0328.json','rb','utf8').read()
            voice_json = json.loads(voice_dat)
            if '#' in word:
                p = re.compile(r'.*#(.*)#.*')
                cv = p.sub(r'\1', word)
                voice_json = [j for j in voice_json if cv in j['title']]
            voice_dic = random.choice(voice_json)
            return getReplyXml_music(soup, voice_dic)
        if u'跟你睡' in word:
            import codecs, json, random
            voice_dat = codecs.open('/alidata1/pujiahh/weixin/voice_gf.json','rb','utf8').read()
            voice_json = json.loads(voice_dat)
            voice_dic = random.choice(voice_json)
            return getReplyXml_music(soup, voice_dic)
        if u'最新汉化' in word:
            games = Games.objects.select_related().filter(post='1', state='1').order_by('-publish_time', '-add_time')[:10]
        else:
            games = Games.objects.select_related().filter(Q(post='1', state='1'),Q(title_cn__icontains = word)).order_by('-publish_time', '-add_time')[:10]
        if games:
            return getReplyXml_games(soup, games)
        else:
            topics = Topic.objects.select_related().filter(subject__icontains = word)[:10]
            if topics:
                return getReplyXml_topics(soup, topics)
            else:
                return getReplyXml_text(soup, u'未能匹配关键词，你可以尝试：\r\n'+tips)

    if soup.msgtype.text == 'event':
        if soup.event.text == 'subscribe':
            return getReplyXml_text(soup, u'感谢您的关注！现在你可以：\r\n'+tips)

def responseMsg(request):
    tips = u'①回复“最新汉化”查询最新发布的汉化游戏。\n②回复游戏名称（如：弹丸论破）查询此游戏的相关汉化资讯和下载。\n③回复“陪我睡”可进入淑女模式。\n④回复“跟你睡”可进入绅士模式。'
    from BeautifulSoup import BeautifulSoup
    soup = BeautifulSoup(request.raw_post_data)
    if soup.msgtype.text == 'text':
        word = soup.content.text
        if u'陪我睡' in word:
            import codecs, json, random, re
            voice_dat = codecs.open('/alidata1/pujiahh/weixin/voice0328.json','rb','utf8').read()
            voice_json = json.loads(voice_dat)
            if '#' in word:
                p = re.compile(r'.*#(.*)#.*')
                cv = p.sub(r'\1', word)
                voice_json = [j for j in voice_json if cv in j['title']]
            voice_dic = random.choice(voice_json)
            return getReplyXml_music(soup, voice_dic)
        if u'跟你睡' in word:
            import codecs, json, random
            voice_dat = codecs.open('/alidata1/pujiahh/weixin/voice_gf.json','rb','utf8').read()
            voice_json = json.loads(voice_dat)
            voice_dic = random.choice(voice_json)
            return getReplyXml_music(soup, voice_dic)
        if u'最新汉化' in word:
            games = Games.objects.select_related().filter(post='1', state='1').order_by('-publish_time', '-add_time')[:10]
        else:
            games = Games.objects.select_related().filter(Q(post='1', state='1'),Q(title_cn__icontains = word)).order_by('-publish_time', '-add_time')[:10]
        if games:
            return getReplyXml_games(soup, games)
        else:
            topics = Topic.objects.select_related().filter(subject__icontains = word)[:10]
            if topics:
                return getReplyXml_topics(soup, topics)
            else:
                return getReplyXml_text(soup, u'未能匹配关键词，你可以尝试：\r\n'+tips)

    if soup.msgtype.text == 'event':
        if soup.event.text == 'subscribe':
            return getReplyXml_text(soup, u'感谢您的关注！现在你可以：\r\n'+tips)


def getReplyXml_text(soup, replyContent):
    extTpl = u'<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>1</FuncFlag></xml>'
    extTpl = extTpl % (soup.fromusername.text, soup.tousername.text, str(int(time.time())), replyContent)
    return extTpl

def getReplyXml_games(soup, games):
    xml_head = u'<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[news]]></MsgType><ArticleCount>%d</ArticleCount><Articles>'%(soup.fromusername.text, soup.tousername.text, str(int(time.time())), len(games))
    xml_end = '</Articles><FuncFlag>1</FuncFlag></xml>'
    itemTpl = u'<item><Title><![CDATA[%s]]></Title><Description><![CDATA[%s]]></Description><PicUrl><![CDATA[%s]]></PicUrl><Url><![CDATA[%s]]></Url></item>'
    item = ''
    for game in games:
        game_platform = ''
        for platform in game.platform.all():
            game_platform += '#%s#'%platform
        title = game_platform + game.title_cn + u'汉化版'
        description = ''
        picurl = 'http://www.pujia8.com/static/%s'%game.imagefile
        url = 'http://www.pujia8.com/library/%d/'%game.id
        item += itemTpl %(title, description, picurl, url)
    return xml_head + item + xml_end

def getReplyXml_topics(soup, topics):
    xml_head = u'<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[news]]></MsgType><ArticleCount>%d</ArticleCount><Articles>'%(soup.fromusername.text, soup.tousername.text, str(int(time.time())), len(topics))
    xml_end = '</Articles><FuncFlag>1</FuncFlag></xml>'
    itemTpl = u'<item><Title><![CDATA[%s]]></Title><Description><![CDATA[%s]]></Description><PicUrl><![CDATA[%s]]></PicUrl><Url><![CDATA[%s]]></Url></item>'
    item = ''
    for topic in topics:
        title = topic.subject
        description = ''
        picurl = 'http://www.pujia8.com/static/%s'%topic.posted_by.get_profile().avatar
        url = 'http://www.pujia8.com/topic/%d/'%topic.id
        item += itemTpl %(title, description, picurl, url)
    return xml_head + item + xml_end

def getReplyXml_music(soup, voice_dic):
    xml_music = u'<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[music]]></MsgType><Music><Title><![CDATA[%s]]></Title><Description><![CDATA[%s]]></Description><MusicUrl><![CDATA[%s]]></MusicUrl><HQMusicUrl><![CDATA[%s]]></HQMusicUrl></Music><FuncFlag>1</FuncFlag></xml>'%(soup.fromusername.text, soup.tousername.text, str(int(time.time())), voice_dic['title'], voice_dic['text'], voice_dic['file'], voice_dic['file'])
    return xml_music


def creatmenu(request):
    appid="wxadc6bf721d3aff46"
    secret="5578f8d944eb16894745ac58224f5211"
    url='https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid='+appid+'&secret='+secret
    response = urllib2.urlopen(url)
    html = response.read()
    tokeninfo = json.loads(html)
    token=tokeninfo['access_token']
    post='''{
                 "button":[
                 {
                      "type":"click",
                      "name":"汉化资讯",
                      "key":"V1001_TODAY_MUSIC"
                  },
                  {
                       "type":"click",
                       "name":"汉化下载",
                       "key":"V1001_TODAY_SINGER"
                  },
                  {
                       "name":"绅士淑女",
                       "sub_button":[
                       {
                           "type":"view",
                           "name":"搜索",
                           "url":"http://www.soso.com/"
                        },
                        {
                           "type":"view",
                           "name":"视频",
                           "url":"http://v.qq.com/"
                        },
                        {
                           "type":"click",
                           "name":"赞一下我们",
                           "key":"V1001_GOOD"
                        }]
                   }]
             }'''
    url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token='+token
    response = urllib2.urlopen(url, post.encode('utf-8'))
    return HttpResponse(response)
