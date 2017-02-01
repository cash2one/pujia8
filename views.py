# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import RequestContext, Template
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

import time, hashlib
from pujiahh.games.models import Games
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

def responseMsg(request):
    from BeautifulSoup import BeautifulSoup
    soup = BeautifulSoup(request.raw_post_data)
    # if soup.event.text == 'subscribe':
    #     return getReplyXml_text(soup, u'感谢关注扑家汉化平台！\
    #         现在回复游戏名称即可查询此游戏的相关汉化资讯和下载。')
    word = soup.content.text
    games = Games.objects.select_related().filter(Q(post='1'),Q(title_cn__icontains = word))
    if games:
        game = games[0]
        title = game.title_cn
        description = game.content[:100]
        picurl = 'http://www.pujiahh.com/static/screenshots/20140228111021_62.jpg'
        url = 'http://www.pujiahh.com/library/1122/'
        return getReplyXml_news(soup, title, description, picurl, url)
    else:
        return getReplyXml_text(soup, u'not found!')

def getReplyXml_text(soup, replyContent):
    extTpl = u'<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>'
    extTpl = extTpl % (soup.fromusername.text, soup.tousername.text, str(int(time.time())), replyContent)
    return extTpl

def getReplyXml_news(soup, title, description, picurl, url):
    extTpl = u'<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[news]]></MsgType><ArticleCount>1</ArticleCount><Articles><item><Title><![CDATA[%s]]></Title><Description><![CDATA[%s]]></Description><PicUrl><![CDATA[%s]]></PicUrl><Url><![CDATA[%s]]></Url></item></Articles><FuncFlag>0</FuncFlag></xml>'
    extTpl = extTpl % (soup.fromusername.text, soup.tousername.text, str(int(time.time())), title, description, picurl, url)
    return extTpl
