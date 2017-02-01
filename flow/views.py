# -*- coding:utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User

from flow.models import *
from pujia_comments.models import *
from account.models import *
import json, re, time, urllib2, StringIO, gzip, random, hashlib, jieba, jieba.analyse
from tagging.models import Tag, TaggedItem
from bs4 import BeautifulSoup

def news_index(request, template_name="flow/index.html"):
    ctx = {
        'flows': Flow.objects.select_related().filter(post=True).order_by('-add_time'),
        'columns': Column.objects.select_related().filter(display=True).order_by('-order')
    }
    return render(request, template_name, ctx)

def news_column(request, column, template_name="flow/index.html"):
    ctx = {
        'flows': Flow.objects.select_related().filter(post=True, column__name=column).order_by('-add_time'),
        'columns': Column.objects.select_related().filter(display=True).order_by('-order')
    }
    return render(request, template_name, ctx)

def news_info(request, fid, template_name="flow/news_info.html"):
    flow = Flow.objects.select_related().get(id = fid)
    flow.count += 1
    flow.save(update_fields = ['count'])
    tags = Tag.objects.get_for_object(flow)
    ctx = {
        'flow': flow,
        'tags': tags,
    }
    return render(request, template_name, ctx)

def tags(request, template_name="flow/tags.html"):
    ctx = {}
    tags = Tag.objects.select_related().all()
    ctx['tags'] = tags
    return render(request, template_name, ctx)

def tag_flows(request, tag_id, template_name="flow/tag_flows.html"):
    ctx = {}
    tag = Tag.objects.select_related().get(pk = tag_id)
    flows = Flow.objects.select_related().filter(post = True).order_by('-add_time')
    flows = TaggedItem.objects.get_by_model(flows, tag)
    if not flows:
        tag.delete()
    ctx['flows'] = flows
    return render(request, template_name, ctx)

def verify(request):
    flows = Flow.objects.select_related().filter(verify = True, post = False).order_by('-add_time')
    n = flows.count()
    if n >= 30:
        flows = random.sample(flows, n/5)
    elif 10 < n < 30:
        flows = random.sample(flows, 4)
    elif 3 < n <= 10:
        flows = random.sample(flows, 3)
    else:
        pass
    for flow in flows:
        flow.post = True
        add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        flow.add_time = add_time
        flow.save(update_fields = ['post', 'add_time'])
        time.sleep(3)
    return HttpResponse('ok')

def make_tag(text, topK = 3):
    return ' '.join(jieba.analyse.textrank(text, topK))

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
    'Referer': 'http://www.baidu.com/',
    'X-Forwarded-For': '93.46.8.89',
    # 'Accept-Encoding': 'deflate, sdch',
}

headers_dmzj = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
    'Referer': 'http://news.dmzj.com/',
    'X-Forwarded-For': '61.135.169.125',
}

headers_bili = {
        'User-Agent':'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293 Safari/6531.22.7',
    }

def random_ip():
    ip = [str(i) for i in random.sample(range(10, 255), 4)]
    return '.'.join(ip)

def get_internet_dat(url, headers = headers):
    req = urllib2.Request(url, None, headers)
    dat = urllib2.urlopen(req).read()
    return dat

def create_user(user_name, avatars_url = '', description = '', ext = False, headers = headers):
    if not User.objects.select_related().filter(username = user_name).exists():
        c = hashlib.md5(user_name.encode('utf8')).hexdigest()
        user = User(username = user_name, password = c, email = '%s@pujia8.com' %c)
        user.save()

        pic_dat = get_internet_dat(avatars_url, headers = headers)
        name = 'static/avatars/' + os.path.basename(avatars_url)
        if ext:
            name += '.jpg'
        fn = os.path.dirname(__file__)[:-4] + name
        dst = open(fn, 'wb')
        dst.write(pic_dat)
        dst.close()

        profile = Profile(user = user, avatar = name[7:], introduce = description)
        profile.save()
    else:
        user = User.objects.select_related().get(username = user_name)
    return user

def save_img(img, headers = headers):
    name = '/static/pics/' + time.strftime('%Y%m%d%H%M%S') + '_%d'% random.randint(0, 100) + '.jpg'
    pic_dat = get_internet_dat(img, headers)
    fn = os.path.dirname(__file__)[:-5] + name
    dst = open(fn, 'wb')
    dst.write(pic_dat)
    return name

def content_save_img(content, headers = headers):
    imgs = content.find_all('img')
    imgs_num = len(imgs)
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
    return content, imgs_num

def random_show_type(imgs_num, isVideo = False):
    if imgs_num >= 3:
        show_type = random.choice(['0', '0', '0', '1', '3', '3'])
    elif 0 < imgs_num < 3:
        show_type = random.choice(['0', '0', '0', '1'])
    else:
        if isVideo:
            show_type = random.choice(['0', '0', '0', '1'])
        else:
            show_type = '0'
    return show_type

def spider_dmzj(url, channels, columns = None):
    content = get_internet_dat(url, headers_dmzj)

    main_page = BeautifulSoup(content, 'html.parser')
    news_div_list = main_page.find_all('div', class_='briefnews_con_li')
    for news_div in news_div_list:
        url = news_div.find('div', class_='li_img_de').find('a').get('href')
        if Flow.objects.select_related().filter(url = url).exists():
            continue
        title = news_div.find('div', class_='li_img_de').find('a').get('title')
        tags = ' '.join([text.string for text in news_div.find_all('span', class_='bqwarp')])
        user_name = news_div.find('p', class_='head_con_p_o').find_all('span')[2].string[3:]

        try:
            content2 = get_internet_dat(url, headers_dmzj)
            content_page = BeautifulSoup(content2, 'html.parser')
            content, imgs_num = content_save_img(content_page.find('div', class_='news_content_con'), headers = headers_dmzj)
            avatars_url = content_page.find('span', class_='v_img').find('img').get('src')
        except:
            continue

        user = create_user(user_name, avatars_url, headers = headers_dmzj)

        add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f = Flow(title = title, content = content, url = url, tags = tags, user = user,
                 show_type = random_show_type(imgs_num), add_time = add_time, verify = True, post = False)
        f.save()

        for channel in channels:
            c = Channel.objects.select_related().get(name = channel)
            f.channel.add(c)
        if columns:
            for column in columns:
                c = Column.objects.select_related().get(name = column)
                f.column.add(c)
        time.sleep(3)
    return 'ok'

def spider_tencentComic(url, channels, columns = None):
    content = get_internet_dat(url)
    main_page = BeautifulSoup(content, 'html.parser', from_encoding='gb2312')
    news_div_list = main_page.find_all('div', class_='Q-tpList')
    for news_div in news_div_list:
        url = 'http://comic.qq.com' + news_div.find('a', class_='pic').get('href')
        if Flow.objects.select_related().filter(url = url).exists():
            continue
        title = unicode(news_div.find('div', class_='newsContent').string)
        content2 = get_internet_dat(url)
        content_page = BeautifulSoup(content2, 'html.parser', from_encoding='gbk')
        content = content_page.find('div', id='Cnt-Main-Article-QQ')
        n = len(content.select('p'))
        if content.select('p:nth-of-type(' + str(n) + ')')[0].string == ' ':
            content.select('p:nth-of-type(' + str(n) + ')')[0].decompose()
        else:
            n += 1
        content.select('p:nth-of-type(' + str(n - 1) + ')')[0].decompose()
        content.select('p:nth-of-type(' + str(n - 2) + ')')[0].decompose()
        content, imgs_num = content_save_img(content)

        user = User.objects.select_related().get(username = u'腾讯动漫')

        add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f = Flow(title = title, content = content, url = url, tags = make_tag(title), user = user,
                 show_type = random_show_type(imgs_num), add_time = add_time, verify = True, post = False)
        f.save()

        for channel in channels:
            c = Channel.objects.select_related().get(name = channel)
            f.channel.add(c)
        if columns:
            for column in columns:
                c = Column.objects.select_related().get(name = column)
                f.column.add(c)
        time.sleep(3)
    return 'ok'

def spider_tgbus(url, channels, columns = None):
    content = get_internet_dat(url)
    main_page = BeautifulSoup(content, 'html.parser', from_encoding='gbk')
    main_div = main_page.find('div', class_='list')
    news_div_list = main_div.find_all('li')
    for news_div in news_div_list:
        url = news_div.find('b').find('a').get('href')
        if news_div.find('font'):
            isInMainPage = 1
        else:
            isInMainPage = 0
        try:
            title = unicode(news_div.find('b').find('a').string)
            if Flow.objects.select_related().filter(url=url).exists() or Flow.objects.select_related().filter(title=title).exists():
                continue
            content2 = get_internet_dat(url)
            content_page = BeautifulSoup(content2, 'html.parser', from_encoding='gbk')
            sourceContent = content_page.find('div', class_='text')
            while sourceContent.find('embed'):
                vWidth = sourceContent.find('embed').get('width')
                vSrc = sourceContent.find('embed').get('src')[:-6].replace('player.php/sid', 'embed')
                vHeight = sourceContent.find('embed').get('height')
                youkuiframeP = content_page.new_tag('p', align="center")
                youkuiframe = content_page.new_tag('iframe', height=vHeight, width=vWidth, src=vSrc, frameborder=0,
                                                   allowfullscreen='allowfullscreen')
                youkuiframeP.append(youkuiframe)
                sourceContent.find('embed').parent.replace_with(youkuiframeP)

            while sourceContent.find('script', src='', string=re.compile('youkuplayer')):
                pattern = re.compile(r"vid: '[A-Za-z0-9=]{15}',")
                vSrc = 'http://player.youku.com/embed/' + pattern.search(
                    sourceContent.find('script', src='').string).group()[6:-2] + '=='
                youkuiframeP = content_page.new_tag('p', align="center")
                youkuiframe = content_page.new_tag('iframe', width='480px', height='400px', src=vSrc, frameborder=0,
                                                   allowfullscreen='allowfullscreen')
                youkuiframeP.append(youkuiframe)
                sourceContent.find('script', src='').replace_with(youkuiframeP)
            map(lambda x: x.decompose(), sourceContent.find_all('script'))
            map(lambda x: x.decompose(), sourceContent.find_all('div', id=re.compile('youkuplayer')))

            if sourceContent.find('p', class_="contentpager"):
                url_list = set(
                    map(lambda x: x.get('href'), sourceContent.find('p', class_="contentpager").find_all('a')))
                sourceContent.find('p', class_="contentpager").decompose()
                for otherPage in url_list:
                    content3 = get_internet_dat(otherPage)
                    content_page = BeautifulSoup(content3, 'html.parser', from_encoding='gbk')
                    otherContent = []
                    for p in content_page.find_all('p'):
                        if p.get('class'):
                            break
                        otherContent.append(p)
                    content_page.find('p', class_="contentpager").decompose()
                    content_page.find('p', class_="editor fr").decompose()
                    sourceContent = unicode(sourceContent) + reduce(lambda x, y: unicode(x) + unicode(y), otherContent)
                sourceContent = BeautifulSoup(sourceContent, 'html.parser')
            content, imgs_num = content_save_img(sourceContent)
        except:
            continue

        user = User.objects.select_related().get(username = u'电玩巴士')

        add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f = Flow(title = title, content = content, url = url, tags = make_tag(title), user = user,
                 show_type = random_show_type(imgs_num), add_time = add_time, verify = True, post = False)
        if isInMainPage:
            f.hot = True
        f.save()

        for channel in channels:
            c = Channel.objects.select_related().get(name = channel)
            f.channel.add(c)

        if columns:
            for column in columns:
                c = Column.objects.select_related().get(name = column)
                f.column.add(c)
        time.sleep(3)
    return 'ok'

def spider_tgbus_ps4_xbox(url, channels, columns = None):
    content = get_internet_dat(url)
    main_page = BeautifulSoup(content, 'html.parser', from_encoding='gbk')
    main_div = main_page.find('div', class_='art-list')
    news_div_list = main_div.find_all('dl')
    for news_div in news_div_list:
        url = news_div.find('dd').find('a').get('href')

        if news_div.find('font'):
            isInMainPage = 1
        else:
            isInMainPage = 0

        try:
            title = unicode(news_div.find('dd').find('a').string)
            if Flow.objects.select_related().filter(url=url).exists() or Flow.objects.select_related().filter(title=title).exists():
                continue
            content2 = get_internet_dat(url)
            content_page = BeautifulSoup(content2, 'lxml', from_encoding='gbk')
            sourceContent = content_page.find('div', class_='art-box', id='body')

            while sourceContent.find('embed'):
                vWidth = sourceContent.find('embed').get('width')
                vSrc = sourceContent.find('embed').get('src')[:-6].replace('player.php/sid', 'embed')
                vHeight = sourceContent.find('embed').get('height')
                youkuiframeP = content_page.new_tag('p', align="center")
                youkuiframe = content_page.new_tag('iframe', height=vHeight, width=vWidth, src=vSrc, frameborder=0,
                                                   allowfullscreen='allowfullscreen')
                youkuiframeP.append(youkuiframe)
                sourceContent.find('embed').parent.replace_with(youkuiframeP)

            while sourceContent.find('script', src='', string=re.compile('youkuplayer')):
                pattern = re.compile(r"vid: '[A-Za-z0-9=]{15}',")
                vSrc = 'http://player.youku.com/embed/' + pattern.search(
                    sourceContent.find('script', src='').string).group()[6:-2] + '=='
                youkuiframeP = content_page.new_tag('p', align="center")
                youkuiframe = content_page.new_tag('iframe', width='480px', height='400px', src=vSrc, frameborder=0,
                                                   allowfullscreen='allowfullscreen')
                youkuiframeP.append(youkuiframe)
                sourceContent.find('script', src='').replace_with(youkuiframeP)
            map(lambda x: x.decompose(), sourceContent.find_all('script'))
            map(lambda x: x.decompose(), sourceContent.find_all('div', id=re.compile('youkuplayer')))

            if sourceContent.find('p', class_="contentpager"):
                url_list = set(
                    map(lambda x: x.get('href'), sourceContent.find('p', class_="contentpager").find_all('a')))
                sourceContent.find('p', class_="contentpager").decompose()
                for otherPage in url_list:
                    content3 = get_internet_dat(otherPage)
                    content_page = BeautifulSoup(content3, 'html.parser', from_encoding='gbk')
                    otherContent = []
                    for p in content_page.find_all('p'):
                        if p.get('class'):
                            break
                        otherContent.append(p)
                    content_page.find('p', class_="contentpager").decompose()
                    content_page.find('p', class_="editor fr").decompose()
                    sourceContent = unicode(sourceContent) + reduce(lambda x, y: unicode(x) + unicode(y), otherContent)
                sourceContent = BeautifulSoup(sourceContent, 'html.parser')
            content, imgs_num = content_save_img(sourceContent)
        except:
            continue

        user = User.objects.select_related().get(username = u'电玩巴士')

        add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f = Flow(title = title, content = content, url = url, tags = make_tag(title), user = user,
                 show_type = random_show_type(imgs_num), add_time = add_time, verify = True, post = False)

        if isInMainPage:
            f.hot = True
        f.save()

        for channel in channels:
            c = Channel.objects.select_related().get(name = channel)
            f.channel.add(c)

        if columns:
            for column in columns:
                c = Column.objects.select_related().get(name = column)
                f.column.add(c)
        time.sleep(3)

    return 'ok'

def spider_toutiao(toutiaohaos, channels, columns = None, verify = True):
    info_list = []
    headers['X-Forwarded-For'] = random_ip()
    for toutiaohao in toutiaohaos:
        mp_info = json.loads(urllib2.urlopen('http://lf.snssdk.com/entry/profile/v1/?entry_id=%s'%toutiaohao[1:]).read())['data']
        user_name = mp_info['name']
        avatars_url = mp_info['icon']
        description = mp_info['description']
        user = create_user(user_name, avatars_url, description, True, headers)

        soup = BeautifulSoup(get_internet_dat('http://toutiao.com/%s/'%toutiaohao, headers), 'lxml')
        articles = soup.find_all(attrs={'class' : re.compile("^title-box link$")})
        urls = []
        for article in articles:
            url = article.get('href')
            if url not in urls:
                urls.append(url)
                info_list.append({
                    'url': url,
                    'user': user,
                    })

    length = len(info_list)
    for i in xrange(length):
        info = random.choice(info_list)
        info_list.remove(info)
        url = info['url']
        if Flow.objects.select_related().filter(url = url).exists():
            continue
        try:
            soup = BeautifulSoup(get_internet_dat(url), 'lxml')
            title = soup.find_all(attrs={'class' : re.compile("^title$")})[0].get_text()
            content = soup.find_all(attrs={'class' : re.compile("^article-content$")})[0]
            tags = soup.find_all(attrs={'class' : re.compile("^tag-item$")})
            tags = ' '.join([tag.get_text() for tag in tags]).replace(u'游戏 ', '').replace(u'漫画 ', '').replace(u'手游 ', '').replace(u'游戏机 ', '')
        except:
            continue

        content, imgs_num = content_save_img(content, headers)

        add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f = Flow(title = title, content = content, url = url, tags = tags, user = info['user'],
                 show_type = random_show_type(imgs_num), add_time = add_time, verify = verify, post = False)
        f.save()

        for channel in channels:
            c = Channel.objects.select_related().get(name = channel)
            f.channel.add(c)
        if columns:
            for column in columns:
                c = Column.objects.select_related().get(name = column)
                f.column.add(c)
        time.sleep(3)
    return 'ok'

def spider_BiliBili(url, channels, columns = None):
    compresseddata = urllib2.urlopen(url).read()
    data = gzip.GzipFile(fileobj = StringIO.StringIO(compresseddata)).read()
    rank_list = json.loads(data)['rank']['list']
    for video in rank_list:
        url = 'http://www.bilibili.com/video/av%s/'%video['aid']
        if Flow.objects.select_related().filter(url = url).exists():
            continue
        isInMainPage = 0
        try:
            if video['play'] < 20000:
                continue
            if video['play'] > 80000:
                isInMainPage = 1
        except:
            continue
        try:
            murl = url.replace('video', 'mobile/video')[:-1] + '.html'
            data = urllib2.urlopen(murl).read()
            soup = BeautifulSoup(data)
            title = video['title']
            content = video['description'].replace('\n', '<br>')
            tags = soup.find_all(attrs={'class' : re.compile("^tag-val$")})
            tags = ' '.join([tag.get_text() for tag in tags])
            user_name = video['author']
            avatars_url = soup.find_all(attrs={'class' : re.compile("^up-pic$")})[0].find_all('img')[0].get('src')
        except:
            continue

        user = create_user(user_name, avatars_url)

        add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f = Flow(title = title, content = content, url = url, tags = tags, user = user,
                 show_type=random_show_type(0, True), add_time = add_time, verify = True, post = False)

        if isInMainPage:
            f.hot = True
        f.save()

        for channel in channels:
            c = Channel.objects.select_related().get(name = channel)
            f.channel.add(c)
        if columns:
            for column in columns:
                c = Column.objects.select_related().get(name = column)
                f.column.add(c)

        time.sleep(3)
    return 'ok'

def spider_gamesky(url, channels, columns = None):
    content = get_internet_dat(url)
    main_page = BeautifulSoup(content, 'lxml')
    main_div = main_page.find('ul', class_='pictxt')
    news_div_list = main_div.find_all('li')

    mainreq = get_internet_dat('http://www.gamersky.com/')
    main_gamesky = BeautifulSoup(mainreq, 'html.parser')
    ul_list = main_gamesky('ul', class_='Ptxt') + main_gamesky('ul', class_='Mid3Lpic_txt')
    a_list = set(map(lambda x: x.get('href'), reduce(lambda x, y: x + y, map(lambda x: x('a'), ul_list))))
    for news_div in news_div_list:
        url = news_div.find('a').get('href')
        if Flow.objects.select_related().filter(url = url).exists():
            continue

        if url in a_list:
            isInMainPage = 1
        else:
            isInMainPage = 0

        try:
            title = unicode(news_div.find('img').get('alt'))
            if u'加速器' in title or u'下载发布' in title:
                continue
            content2 = get_internet_dat(url)
            content_page = BeautifulSoup(content2, 'html.parser')
            tags = ''
            if content_page.find('ul', class_='Relevantlike'):
                tags = ' '.join(map(lambda x: x.string, content_page.find('ul', class_='Relevantlike').find_all('a')))
                if u'官方新闻' in tags:
                    continue
            content = content_page.find('div', class_='Mid2L_con')
            if content.find('div', class_='Mid2L_down'):
                content.find('div', class_='Mid2L_down').decompose()
            while content.find('script', src=''):
                pattern = re.compile(r'http://player.youku.com/embed/[A-Za-z0-9=]{17}')
                patternH = re.compile(r'height=\\"[0-9]+\\"')
                patternW = re.compile(r'width=\\"[0-9]+\\"')
                vHeight = patternH.search(content.find('script', src='').string).group()[9:-2]
                vWidth = patternW.search(content.find('script', src='').string).group()[8:-2]
                vSrc = pattern.search(content.find('script', src='').string).group()
                youkuiframeP = content_page.new_tag('p', align="center")
                youkuiframe = content_page.new_tag('iframe', height=vHeight, width=vWidth, src=vSrc, frameborder=0,
                                                   allowfullscreen='allowfullscreen')
                youkuiframeP.append(youkuiframe)
                content.find('script', src='').parent.replace_with(youkuiframeP)
            for useless in content.find_all('a', class_='n1'):
                if useless.parent:
                    useless.parent.decompose()
            if content.find('span', id='pe100_page_contentpage').find('a'):
                url_list = set(
                    map(lambda x: x.get('href'), content.find('span', id='pe100_page_contentpage').find_all('a')))
                url_list.remove(url)
                content.find('span', id='pe100_page_contentpage').decompose()
                for otherPage in url_list:
                    content3 = get_internet_dat(otherPage)
                    content_page = BeautifulSoup(content3, 'html.parser')
                    for useless in content_page.find_all('a', class_='n1'):
                        if useless.parent:
                            useless.parent.decompose()
                    content = unicode(content) + reduce(lambda x, y: unicode(x) + unicode(y), content_page.find_all('p'))
                content = BeautifulSoup(content, 'html.parser')

            content, imgs_num = content_save_img(content)
        except:
            continue

        user = User.objects.select_related().get(username = u'游民星空')

        add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f = Flow(title = title, content = content, url = url, tags = tags, user = user,
                 show_type = random_show_type(imgs_num), add_time = add_time, verify = True, post = False)

        # if isInMainPage:
        #     f.hot = True
        f.save()

        for channel in channels:
            c = Channel.objects.select_related().get(name = channel)
            f.channel.add(c)
        if columns:
            for column in columns:
                c = Column.objects.select_related().get(name = column)
                f.column.add(c)
        time.sleep(3)
    return 'ok'

def spider_gameskyacg(url, channels, columns = None):
    content = get_internet_dat(url)
    main_page = BeautifulSoup(content, 'html.parser')
    main_div = main_page.find('ul', class_='pictxt')
    news_div_list = main_div.find_all('li')

    mainreq = get_internet_dat('http://www.gamersky.com/')
    main_gamesky = BeautifulSoup(mainreq, 'html.parser')
    ul_list = main_gamesky('ul', class_='Ptxt') + main_gamesky('ul', class_='Mid3Lpic_txt')
    a_list = set(map(lambda x: x.get('href'), reduce(lambda x, y: x + y, map(lambda x: x('a'), ul_list))))

    for news_div in news_div_list:
        url = news_div.find('a').get('href')
        if url in a_list:
            isInMainPage = 1
        else:
            isInMainPage = 0

        if Flow.objects.select_related().filter(url = url).exists():
            continue

        try:
            title = unicode(news_div.find('a').get('title'))
            content2 = get_internet_dat(url)
            content_page = BeautifulSoup(content2, 'html.parser')

            tags = ''
            if content_page.find('ul',class_='Relevantlike'):
                tags = ' '.join(map(lambda x:x.string,content_page.find('ul',class_='Relevantlike').find_all('a')))
                if u'官方新闻' in tags:
                    continue

            content = content_page.find('div', class_='MidL_con')
            if content.find('div', class_='Mid2L_down'):
                content.find('div', class_='Mid2L_down').decompose()

            while content.find('script', string=True):
                pattern = re.compile(r'http://player.youku.com/embed/[A-Za-z0-9=]{17}')
                patternH = re.compile(r'height=\\"[0-9]+\\"')
                patternW = re.compile(r'width=\\"[0-9]+\\"')
                vHeight = patternH.search(content.find('script', src='').string).group()[9:-2]
                vWidth = patternW.search(content.find('script', src='').string).group()[8:-2]
                vSrc = pattern.search(content.find('script', src='').string).group()
                youkuiframeP = content_page.new_tag('p', align="center")
                youkuiframe = content_page.new_tag('iframe', height=vHeight, width=vWidth, src=vSrc, frameborder=0,
                                                   allowfullscreen='allowfullscreen')
                youkuiframeP.append(youkuiframe)
                content.find('script', src='').parent.replace_with(youkuiframeP)
            for useless in content.find_all('a', class_='n1'):
                if useless.parent:
                    useless.parent.decompose()
            if content.find('span', id='pe100_page_contentpage').find('a'):
                url_list = set(
                    map(lambda x: x.get('href'), content.find('span', id='pe100_page_contentpage').find_all('a')))
                url_list.remove(url)
                content.find('span', id='pe100_page_contentpage').decompose()
                for otherPage in url_list:
                    content3 = get_internet_dat(otherPage)
                    content_page = BeautifulSoup(content3, 'html.parser')
                    for useless in content_page.find_all('a', class_='n1'):
                        if useless.parent:
                            useless.parent.decompose()
                    content = unicode(content) + reduce(lambda x, y: unicode(x) + unicode(y),
                                                        content_page.find_all('p'))
                content = BeautifulSoup(content, 'html.parser')
            content, imgs_num = content_save_img(content)

        except:
            continue

        user = User.objects.select_related().get(username=u'游民星空')

        add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f = Flow(title=title, content=content, url=url, tags=tags, user=user,
                 show_type=random_show_type(imgs_num), add_time=add_time, verify=True, post=False)

        # if isInMainPage:
        #     f.hot = True
        f.save()

        for channel in channels:
            c = Channel.objects.select_related().get(name=channel)
            f.channel.add(c)
        if columns:
            for column in columns:
                c = Column.objects.select_related().get(name=column)
                f.column.add(c)
        time.sleep(3)
    return 'ok'

def spider_178(url, channels, columns = None):
    content = get_internet_dat(url)
    main_page = BeautifulSoup(content, 'html.parser')
    main_div = main_page.find('div', class_='imgtextlist')
    news_div_list = main_div.find_all('div', class_='imgbox')
    for news_div in news_div_list:
        url = news_div.find('a').get('href')
        if Flow.objects.select_related().filter(url = url).exists():
            continue
        try:
            title = unicode(news_div.find('img').get('alt'))
            # 178每个新闻都有专门制作的头图大小固定而且没有水印，地址储存为head_image
            head_image = news_div.find('img').get('src')
            content2 = get_internet_dat(url)
            content_page = BeautifulSoup(content2, 'html.parser')
            content = content_page.find('div', class_='artical-content')
            # video_list 为新闻中附带的b站视频的地址
            video_list = []
            while content.find('embed'):
                if content.find('embed').get('flashvars'):
                    video_url = 'http://www.bilibili.com/video/av' + \
                                content.find('embed').get('flashvars')[4:content.find('embed').get('flashvars').find('&')]
                    video_list.append(video_url)
                content.find('embed').parent.decompose()
            content, imgs_num = content_save_img(content)
        except:
            continue

        user = User.objects.select_related().get(username = u'178acg')

        add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f = Flow(title = title, content = content, url = url, tags = make_tag(title), user = user,
                 show_type = random_show_type(imgs_num), add_time = add_time, verify = True, post = False)
        f.save()

        for channel in channels:
            c = Channel.objects.select_related().get(name = channel)
            f.channel.add(c)
        if columns:
            for column in columns:
                c = Column.objects.select_related().get(name = column)
                f.column.add(c)
        time.sleep(3)
    return 'ok'

def spider_appgame_jp(url, channels, columns = None):
    content = get_internet_dat(url)
    main_page = BeautifulSoup(content, 'html.parser')
    main_div = main_page.find('ul', class_='jp_arclist')
    news_div_list = main_div.find_all('li')
    for news_div in news_div_list:
        url = news_div.find('a').get('href')
        if Flow.objects.select_related().filter(url = url).exists():
            continue
        title = unicode(news_div.find('a').get('title'))
        content2 = get_internet_dat(url)
        content_page = BeautifulSoup(content2, 'html.parser')
        author_name = unicode(content_page.find('dl', class_='jp_article_d').find('a').string)
        author_describe = unicode(content_page.find('dl', class_='jp_article_d').find('p').string)
        author_face = 'http://jp.appgame.com' + content_page.find('dl', class_='jp_article_d').find('img', class_='avatar').get('src')
        sourceContent = content_page.find('div', class_='jp_article')

        while sourceContent.find('div', class_='appgame-player-content'):
            vSrc = 'http://player.youku.com/embed/' + sourceContent.find('div', class_='appgame-player-content').get('id')[23:] + '=='
            youkuiframeP = content_page.new_tag('p', align="center")
            youkuiframe = content_page.new_tag('iframe', width='480px', height='400px', src=vSrc, frameborder=0, allowfullscreen='allowfullscreen')
            youkuiframeP.append(youkuiframe)
            sourceContent.find('div', class_='appgame-player-content').replace_with(youkuiframeP)

        sourceContent = sourceContent.find_all('p')[:-1]
        content = BeautifulSoup('', 'html.parser')
        for element in sourceContent:
            content.append(element)
        content, imgs_num = content_save_img(content)

        try:
            user = create_user(author_name, author_face, author_describe)
        except:
            user = User.objects.select_related().get(username=u'任玩堂')

        add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f = Flow(title=title, content=content, url=url, tags=make_tag(title), user=user,
                 show_type=random_show_type(imgs_num), add_time=add_time, verify=True, post=False)
        f.save()

        for channel in channels:
            c = Channel.objects.select_related().get(name = channel)
            f.channel.add(c)
        if columns:
            for column in columns:
                c = Column.objects.select_related().get(name = column)
                f.column.add(c)
        time.sleep(3)
    return 'ok'

def spider_appgame_reviews(url, channels, columns = None):
    content = get_internet_dat(url)
    main_page = BeautifulSoup(content, 'html.parser')
    main_div = main_page.find('div', class_='appgame-items')
    news_div_list = main_div.find_all('div', class_='appgame-item')
    for news_div in news_div_list:
        url = news_div.find(class_='appgame-item-title').find('a').get('href')
        if Flow.objects.select_related().filter(url = url).exists():
            continue
        try:
            title = unicode(news_div.find(class_='appgame-item-title').find('a').string)
            content2 = get_internet_dat(url)
            content_page = BeautifulSoup(content2, 'html.parser')
            sourceContent = content_page.find('div',class_='appgame-primary')
            author_name = content_page.find('div',class_='appgame-footer-author-name').find('a').string
            author_describe = content_page.find('div',class_='appgame-footer-author-describe').string
            author_face = 'http://www.appgame.com/' + content_page.find('div',class_='appgame-footer-author-face').find('img').get('src')
            def is_text(css_class):
                return css_class is  None or css_class == 'redtitle'
            sourceContent = sourceContent.find_all(['p','div'],class_=is_text)[:-2]
            content = BeautifulSoup('','html.parser')
            for element in sourceContent:
                content.append(element)
            content, imgs_num = content_save_img(content)

        except:
            continue

        try:
            user = create_user(author_name, author_face, author_describe)
        except:
            user = User.objects.select_related().get(username=u'任玩堂')

        add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f = Flow(title=title, content=content, url=url, tags=make_tag(title), user=user,
                 show_type=random_show_type(imgs_num), add_time=add_time, verify=True, post=False)
        f.save()

        for channel in channels:
            c = Channel.objects.select_related().get(name=channel)
            f.channel.add(c)
        if columns:
            for column in columns:
                c = Column.objects.select_related().get(name=column)
                f.column.add(c)
        time.sleep(3)
    return 'ok'

def spider_youkuacg(url, channels, columns = None):
    content = get_internet_dat(url)
    main_page = BeautifulSoup(content, 'html.parser')
    main_div = main_page.find('div', id='m_213785')
    news_div_list = main_div.find_all('div', class_='v')
    for news_div in news_div_list:
        url = news_div.find('a').get('href')
        if Flow.objects.select_related().filter(url = url).exists():
            continue
        tags = unicode(news_div.find('img').get('alt'))
        head_img = save_img(news_div.find('img').get('_src'))
        content2 = get_internet_dat(url)
        content_page = BeautifulSoup(content2, 'html.parser')
        title = content_page.find('h1', class_='title').find('a').get('title') + u'：' + \
                content_page.find('span',id='subtitle').get('title')
        content = content_page.find('input', id='link4').get('value')


        user = User.objects.select_related().get(username=u'优酷')

        add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f = Flow(title=title, content=content, url=url, tags=tags, head_img=head_img, user=user,
                 show_type='0', add_time=add_time, verify=True, post=False)
        f.save()

        for channel in channels:
            c = Channel.objects.select_related().get(name=channel)
            f.channel.add(c)
        if columns:
            for column in columns:
                c = Column.objects.select_related().get(name=column)
                f.column.add(c)
        time.sleep(3)
    return 'ok'

def spider_a9vg(url, channels, columns = None):
    content = get_internet_dat(url)
    main_page = BeautifulSoup(content, 'html.parser')
    main_div = main_page.find('div', class_='list')
    news_div_list = main_div.find_all('dl', class_='cl')
    for news_div in news_div_list:
        url = news_div.find('dt').find('a').get('href')

        if Flow.objects.select_related().filter(url = url).exists():
            if columns:
                flow = Flow.objects.select_related().get(url = url)
                for column in columns:
                    c = Column.objects.select_related().get(name=column)
                    if c not in flow.column.all():
                        flow.column.add(c)
            continue

        title = unicode(news_div.find('img').get('alt'))
        content2 = get_internet_dat(url)
        content_page = BeautifulSoup(content2, 'html.parser')
        content = content_page.find('div', class_='article-body')

        while content.find('object'):
            vHeight = content.find('object').get('height')
            vWidth = content.find('object').get('width')
            vSrc = content.find('embed').get('src')[:-6].replace('/player.php/sid/', '/embed/')
            youkuiframe = content_page.new_tag('iframe', height=vHeight, width=vWidth, src=vSrc, frameborder=0,
                                               allowfullscreen='allowfullscreen')
            content.find('object').replace_with(youkuiframe)
        content, imgs_num = content_save_img(content)

        user = User.objects.select_related().get(username=u'A9VG电玩部落')

        add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f = Flow(title=title, content=content, url=url, tags=make_tag(title), user=user,
                 show_type=random_show_type(imgs_num), add_time=add_time, verify=True, post=False)
        f.save()

        for channel in channels:
            c = Channel.objects.select_related().get(name=channel)
            f.channel.add(c)
        if columns:
            for column in columns:
                c = Column.objects.select_related().get(name=column)
                f.column.add(c)
        time.sleep(3)
    return 'ok'

def spider_Bili(request):
    url = request.GET.get('url')
    if not Flow.objects.select_related().filter(url = url).exists():
        content = get_internet_dat(url, headers_bili)
        main_page = BeautifulSoup(content, 'html.parser')
        news_div = main_page.find('div', class_='video-info')
        title = news_div.find('h1', class_='video-title').get('title')
        content = unicode(news_div.find('div', class_='video-desc'))
        tags = ' '.join([text.string for text in main_page.find_all('a', class_='tag-val')])
        user_name = news_div.find('a', class_='up-name').string[5:]
        avatars_url = news_div.find('div', class_='up-pic').find('img').get('src')

        user = create_user(user_name, avatars_url, headers = headers_bili)

        add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f = Flow(title = title, content = content, url = url, tags = tags, user = user, add_time = add_time, post = False)
        f.save()

        return HttpResponse('收录完成')
    else:
        return HttpResponse('此视频已收录')

def spider(request, type):
    if type == 'game':
        #游戏：游侠 触乐 机核 游戏时光vgtime NGA玩家社区 着迷网 游戏陀螺 游戏早知道 有趣点 二柄游戏 电游者 九游 电游风云 游研社
        #游戏茶馆 多玩 A9VG电玩部落 游迅网 3DMGAME 游戏机实用技术 杉果游戏Sonkwo CBI游戏天地 新浪游戏
        spider_toutiao(['m4165916636', 'm3141132433', 'm5564403914', 'm5071790849', 'm6063361128', \
                        'm3217797837', 'm3455496941', 'm3825914808', 'm4318088870', 'm3486628556', 'm3371735531', 'm5487235067', \
                        'm4385932506', 'm6619511247', 'm4217939356', 'm6113840992', 'm5439041636', 'm3359945322', 'm6566863607', \
                        'm4307400726', 'm4343802237', 'm6573392920', 'm5495162382'], [u'游戏'], verify = False)
        spider_BiliBili('http://www.bilibili.com/index/rank/all-03-4.json', [u'游戏', u'视频'])

    if type == 'tgbus':
        spider_tgbus('http://3ds.tgbus.com/news/', [u'游戏'], [u'任天堂'])
        spider_tgbus('http://wiiu.tgbus.com/news/', [u'游戏'], [u'任天堂'])
        spider_tgbus('http://psv.tgbus.com/news/', [u'游戏'], [u'索尼'])
        spider_tgbus_ps4_xbox('http://ps4.tgbus.com/news/', [u'游戏'], [u'索尼'])
        spider_tgbus_ps4_xbox('http://xboxone.tgbus.com/news/', [u'游戏'], [u'微软'])

    if type == 'gamesky':
        spider_gamesky('http://www.gamersky.com/news/pc/zx/', [u'游戏'], [u'PC'])
        spider_gamesky('http://tv.gamersky.com/ps/', [u'游戏'], [u'索尼'])
        spider_gamesky('http://tv.gamersky.com/xbox/', [u'游戏'], [u'微软'])
        spider_gamesky('http://shouyou.gamersky.com/zx/', [u'游戏'], [u'手游'])
        spider_gameskyacg('http://acg.gamersky.com/news/', [u'动漫'], [u'动漫'])

    if type == 'a9vg':
        spider_a9vg('http://www.a9vg.com/ps4/', [u'游戏'], [u'索尼'])
        spider_a9vg('http://www.a9vg.com/xboxone/', [u'游戏'], [u'微软'])
        spider_a9vg('http://www.a9vg.com/wiiu/', [u'游戏'], [u'任天堂'])

    if type == 'appgame':
        spider_appgame_jp('http://jp.appgame.com/archives/category/newgame', [u'游戏'], [u'手游'])
        spider_appgame_jp('http://jp.appgame.com/archives/category/mainstream', [u'游戏'], [u'手游'])
        spider_appgame_jp('http://jp.appgame.com/archives/category/nijigen', [u'游戏'], [u'手游'])
        spider_appgame_reviews('http://www.appgame.com/archives/category/game-reviews', [u'游戏'], [u'手游'])

    if type == 'comic':
        #动漫：宅腐动漫社 每日漫画 漫画社 追动漫 王重阳道长 动漫主宰系领域 动漫东东 二次元观察
        # spider_toutiao(['m6098511513', 'm6134625457', 'm6205801402', 'm4673174445', 'm4457854996', 'm6170783387', 'm5959258501', \
        #                 'm5561796074'], [u'动漫'], [u'漫画'])
        #动漫：半次元 COS联盟 cos二次元 推软妹君
        # spider_toutiao(['m6018247938', 'm6171695752', 'm6700392018', 'm6836751208'], [u'动漫'], [u'COS'])
        spider_tencentComic('http://comic.qq.com/c/dmlist_1.htm', [u'动漫'], [u'动漫'])
        spider_tencentComic('http://comic.qq.com/c/dmlist1_1.htm', [u'动漫'], [u'动漫'])
        spider_tencentComic('http://comic.qq.com/c/dmlistyj_1.htm', [u'动漫'], [u'动漫'])
        spider_178('http://acg.178.com/list/262377910211.html', [u'动漫'], [u'COS'])
        spider_178('http://acg.178.com/list/goods/index.html', [u'动漫'], [u'周边'])
        spider_dmzj('http://news.dmzj.com/donghuaqingbao', [u'动漫'], [u'动漫'])
        spider_dmzj('http://news.dmzj.com/manhuaqingbao', [u'动漫'], [u'动漫'])
        spider_dmzj('http://news.dmzj.com/manhuazhoubian', [u'动漫'], [u'周边'])
        spider_dmzj('http://news.dmzj.com/shengyouqingbao', [u'动漫'], [u'动漫'])
        spider_dmzj('http://news.dmzj.com/yinyuezixun', [u'动漫'], [u'动漫'])

    if type == 'douga':
        # 动漫：GACHA二次元社区 次元喵 动漫艺术家 一万光年动漫电台 萌娘ACG研究所 猫叔聊动漫
        # spider_toutiao(['m5899401947', 'm6962457871', 'm6086980938', 'm5921285299', 'm5890379241', 'm6463386991'], [u'动漫'], [u'动漫资讯'])
        spider_BiliBili('http://www.bilibili.com/index/rank/all-03-1.json', [u'动漫'], [u'动画'])
        spider_178('http://acg.178.com/list/88134860671.html', [u'动漫'], [u'动漫'])
        # spider_youkuacg('http://comic.youku.com/', [u'动漫'], [u'新番'])

    return HttpResponse('ok')

