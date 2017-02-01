import re
import string
from django.contrib.auth.models import User
from django.core.cache import cache

LEADING_PUNCTUATION  = ['(', '<', '&lt;']
TRAILING_PUNCTUATION = ['.', ',', ')', '>', '\n', '&gt;']
punctuation_re = re.compile('^(?P<lead>(?:%s)*)(?P<middle>.*?)(?P<trail>(?:%s)*)$' %\
                            ('|'.join([re.escape(x) for x in LEADING_PUNCTUATION]),
                             '|'.join([re.escape(x) for x in TRAILING_PUNCTUATION])))
word_split_re = re.compile(r'(\S+)')
simple_email_re = re.compile(r'^\S+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+$')

def autolink(text, trim_url_limit=None, nofollow=False):
    trim_url = lambda x, limit=trim_url_limit: limit is not None and (x[:limit] + (len(x) >=limit and '...' or ''))  or x
    words = word_split_re.split(text)
    nofollow_attr = nofollow and ' rel="nofollow"' or ''
    for i, word in enumerate(words):
        match = punctuation_re.match(word)
        if match:
            lead, middle, trail = match.groups()
            if middle.startswith('www.') or ('@' not in middle and not middle.startswith('http://') and not middle.startswith('https://') and\
                                             len(middle) > 0 and middle[0] in string.letters + string.digits and\
                                             (middle.endswith('.org') or middle.endswith('.net') or middle.endswith('.com'))):
                middle = '<a href="http://%s"%s target="_blank">%s</a>' % (middle, nofollow_attr, trim_url(middle))
            if middle.startswith('http://') or middle.startswith('https://'):
                middle = '<a href="%s"%s target="_blank">%s</a>' % (middle, nofollow_attr, trim_url(middle))
            if '@' in middle and not middle.startswith('www.') and not ':' in middle\
            and simple_email_re.match(middle):
                middle = '<a href="mailto:%s">%s</a>' % (middle, middle)
            if lead + middle + trail != word:
                words[i] = lead + middle + trail
    return ''.join(words)

def pujia_text(text):
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    _re_imgs = re.compile('(((http[s]?://?[^ \f\n\r\t\v\?]*)|(/static/(upload|uploads|emoji)/[\w]*)).(\.jpg|\.jpeg|\.gif|\.png|\.bmp))', re.UNICODE|re.I|re.M|re.S)
    _re_audio = re.compile('(((http[s]?://?[^ \f\n\r\t\v\?]*)|(/static/upload[s]?/[\w]*)).(mp3|wav|ogg))', re.UNICODE|re.I|re.M|re.S)
    _re_video = re.compile('(((http[s]?://?[^ \f\n\r\t\v\?]*)|(/static/upload[s]?/[\w]*)).mp4)', re.UNICODE|re.I|re.M|re.S)
    _re_link = re.compile('(/static/upload/[\w]*.(zip|rar|gz|7z|apk|ipa))', re.UNICODE|re.I|re.M|re.S)
    _re_strong = re.compile('\[b\]([\S\u3000 ]*)\[/b\]', re.I|re.M|re.S)
    _re_code = re.compile('\[code\]([\S\s]*?)\[/code\]', re.I|re.M|re.S)
    _re_hide_text = re.compile('^//([\S\u3000 ]*)(\r|\n)', re.I|re.M|re.S)
    _re_youku = re.compile('http://v.youku.com/v_show/id_([A-Za-z0-9=]+).html(\?f=[0-9]+)?', re.UNICODE|re.I|re.M|re.S)
    _re_letv = re.compile('http://www.letv.com/ptv/vplay/([A-Za-z0-9]+).html', re.UNICODE|re.I|re.M|re.S)
    _re_qq = re.compile('http://v.qq.com/cover/[A-Za-z0-9]+/[A-Za-z0-9]+\.html\?vid=([A-Za-z0-9]+)', re.UNICODE|re.I|re.M|re.S)
    _re_tudou = re.compile('http://www.tudou.com/(albumplay|programs/view|listplay)/([A-Za-z0-9\=\_\-]+)(/[A-Za-z0-9\=\_\-]+.html|/(\?fr=[A-Za-z0-9\=\_\-]+)?|.html)', re.UNICODE|re.I|re.M|re.S)
    _re_bili = re.compile('http://www.bilibili.(tv|com)/video/av([A-Za-z0-9]+)/', re.UNICODE|re.I|re.M|re.S)
    _re_acfun = re.compile('http://www.acfun.(tv|com)/v/ac([A-Za-z0-9]+)', re.UNICODE|re.I|re.M|re.S)
    _re_vote_weibo = re.compile('&lt;iframe(.*?)&gt;&lt;/iframe&gt;', re.UNICODE|re.I|re.M|re.S)

    if 'src="http://vote.weibo.com/widget?vid=' in text:
        text = _re_vote_weibo.sub(r'<iframe \1></iframe>', text)
    if _re_imgs.search(text):
        text = _re_imgs.sub(r'<img src="\1" alt="" />', text)
    if _re_audio.search(text):
        text = _re_audio.sub(r'<audio src="\1" controls="controls"></audio>', text)
    if _re_video.search(text):
        text = _re_video.sub(r'<video src="\1" controls="controls" preload="preload" width="600"></video>', text)
    if _re_link.search(text):
        text = _re_link.sub(r'<a href="\1">\1</a>', text)
    if '@' in text:
        name_list = re.findall('\@([\S]*)', text)
        for name in  name_list:
            try:
                user = User.objects.select_related().get(username__exact = name)
                text = text.replace('@%s'%name, '@<a href="/user/%s/">%s</a>'%(user.pk, name))
            except:
                pass
    if '[b]' in text and '[/b]' in text:
        text = _re_strong.sub(r'<strong>\1</strong>', text)
    if '[code]' in text and '[/code]' in text:
        text = _re_code.sub(r'<pre>\1</pre>', text)
    if '//' in text:
        text = _re_hide_text.sub(r'//<span class="hide_text">\1</span>\2', text)
    if 'v.youku.com' in text:
        text = _re_youku.sub(r'<embed height=540 width=100% src="https://players.youku.com/player.php/sid/\1/v.swf" frameborder=0 allowfullscreen></embed>', text)
    if 'www.letv.com' in text:
        text = _re_letv.sub(r'<object width="600" height="480"><param name="allowFullScreen" value="true"><param name="flashVars" value="id=\1" /><param name="movie" value="http://i7.imgs.letv.com/player/swfPlayer.swf?autoplay=0" /><embed src="http://i7.imgs.letv.com/player/swfPlayer.swf?autoplay=0" flashVars="id=\1" width="600" height="480" allowFullScreen="true" type="application/x-shockwave-flash" /></object>', text)
    if 'www.tudou.com' in text:
        if 'albumplay' in text:
            text = _re_tudou.sub(r'<embed src="http://www.tudou.com/a/\2/&resourceId=0_05_02_99&iid=130747612&bid=05/v.swf" allowFullScreen="true" quality="high" width="600" height="480" align="middle" allowScriptAccess="sameDomain" type="application/x-shockwave-flash"></embed>', text)
        else:
            text = _re_tudou.sub(r'<embed src="http://www.tudou.com/v/\2/&resourceId=0_05_05_99&iid=152278332&bid=05/v.swf" allowFullScreen="true" quality="high" width="600" height="480" align="middle" allowScriptAccess="sameDomain" type="application/x-shockwave-flash"></embed>', text)
    if 'www.bilibili.' in text:
        text = _re_bili.sub(r'<embed src="https://static-s.bilibili.com/miniloader.swf?aid=\2&page=1" allowscriptaccess="never" allowFullScreen="true" quality="high" flashvars="playMovie=true&auto=1" width="600" height="480" align="middle"  type="application/x-shockwave-flash" wmode="transparent"></embed>', text)
    if 'www.acfun.' in text:
        text = _re_acfun.sub(r'<object type="application/x-shockwave-flash" data="http://static.acfun.mm111.net/player/ACFlashPlayer.out.swf" width="600" height="480"><param name="allowfullscreen" value="true"><param name="allowscriptaccess" value="always"><param name="seamlesstabbing" value="true"><param name="wmode" value="direct"><param name="allowFullscreenInteractive" value="true"><param name="flashvars" value="type=page&url=http://www.acfun.tv/v/ac\2"></object>', text)
    if 'v.qq.com' in text:
        text = _re_qq.sub(r'<iframe frameborder="0" width="600" height="480" src="http://v.qq.com/iframe/player.html?vid=\1&tiny=0&auto=0" allowfullscreen></iframe>', text)
    text = re.sub(r'^\r\n', '', text)
    return autolink(text).replace('\n','<br>')

def gravatar_for_user(user):
    if user:
        avatar_url = cache.get('avatar_url_uid%s'%user.id)
        if not avatar_url:
            avatar = user.get_profile().avatar
            if avatar:
                avatar_url = avatar.url
            else:
                avatar_url = '/static/img/tx.jpg'
            cache.set('avatar_url_uid%s'%user.id, avatar_url, 1800)
    else:
        avatar_url = '/static/img/tx.jpg'
    return avatar_url
