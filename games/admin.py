from models import Platform, Games, QiuHanHua, GameScore, Collection
from django.contrib import admin
from pujia_comments.models import PujiaComment
from PIL import Image
import re, os
from django.core.urlresolvers import reverse

import urllib2, urllib, json, time
import base64
import hashlib
import random

username = "pluto"
passwd = "pluto@VeryCDN"


class Encrypt(object):
    lockstream =  'st=lDEFABCNOPyzghi_jQRST-UwxkVWXYZabcdefIJK6/7nopqr89LMmGH012345uv'

    def encrypt(self, txtStream, public_key):
        # 随机找一个数字，并从密锁串中找到一个密锁值
        lockLen = len(self.lockstream)
        lockCount = random.randint(0, lockLen-1)
        randomLock = self.lockstream[lockCount]
        # 结合随机密锁值生成MD5后的密码
        password = hashlib.md5(public_key + randomLock)
        password_hex = password.hexdigest()
        # 开始对字符串加密
        txtStream = base64.b64encode(txtStream)
        tmpStream = ''
        k = 0
        for i in range(len(txtStream)):
            k = 0 if len(password_hex) == k else k
            j = (self.lockstream.find(txtStream[i]) + lockCount + ord(password_hex[k])) % lockLen
            tmpStream += self.lockstream[j]
            k += 1
        return tmpStream + randomLock

    def decrypt(self, txtStream, public_key):
        lockstream = 'st=lDEFABCNOPyzghi_jQRST-UwxkVWXYZabcdefIJK6/7nopqr89LMmGH012345uv'
        lockLen = len(lockstream)
        txtLen = len(txtStream)
        randomLock = txtStream[txtLen - 1]
        lockCount = lockstream.find(randomLock)
        password = hashlib.md5(public_key + randomLock).hexdigest()
        txtStream = txtStream[0:txtLen - 1]
        tmpStream = ''
        i = 0
        k = 0
        for i in range(i, len(txtStream)):
            k = (0 if k == len(password) else k)
            j = ((lockstream.find(txtStream[i]) - lockCount - ord(password[k])))

            while (j < 0):
                j = j + (lockLen)

            tmpStream += lockstream[j]
            k += 1
        return base64.b64decode(tmpStream)


en_obj = Encrypt()
get_encrypt = en_obj.encrypt(passwd, 'verycloud#cryptpass')

host_api = "https://api3.verycloud.cn"
get_token_api = "/API/OAuth/authorize"
refresh_api = "/API/cdn/refresh"

data = {"username": username, "password": get_encrypt}
headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Accept": "application/json"
}

def fix_pujiahh(modeladmin, request, queryset):
    for game in queryset:
        if 'pujiahh.com' not in game.content and 'pujiahh.com' not in game.download_link:
            continue
        game.content = game.content.replace('pujiahh.com', 'pujia8.com')
        game.download_link = game.download_link.replace('pujiahh.com', 'pujia8.com')
        game.save()
fix_pujiahh.short_description = u'修正域名信息'

def fix_img(modeladmin, request, queryset):
    for game in queryset:
        images_list = re.findall('(/static/[\S]*.[jpg|jpeg|png|PNG])', game.content)
        for img in images_list:
            try:
                fn = os.path.dirname(__file__)[:-6] + img
                im = Image.open(fn)
                width, heigth = im.size
                if width * 16 / heigth <= 9:
                    im = im.resize((600*width/heigth, 600),  Image.ANTIALIAS)
                elif width > 800:
                    im = im.resize((800, 800*heigth/width),  Image.ANTIALIAS)
                im.convert(mode='RGBA').save(fn.replace('.png', '.jpeg').replace('.PNG', '.jpeg'), quality = 80)
                if '.png' in fn or '.PNG' in fn:
                    os.remove(fn)
                    game.content = game.content.replace(img, img.replace('.png', '.jpeg').replace('.PNG', '.jpeg'))
            except:
                pass
        game.save()
fix_img.short_description = u'修正图片'

def fix_dl(modeladmin, request, queryset):
    for game in queryset:
        p = False
        if game.apk_name and 'http' not in game.apk_name:
            game.apk_name = 'http://apk.pujia8.com/apk/%s'%(game.apk_name)
            p = True
        if game.obb_name and 'http' not in game.obb_name:
            game.obb_name = 'http://apk.pujia8.com/obb/%s'%(game.obb_name)
            p = True
        if p:
            game.save()
fix_dl.short_description = u'修正载点'

def fix_dl2(modeladmin, request, queryset):
    for game in queryset:
        p = False
        if game.apk_name and 'http://apk.pujia8.com' in game.apk_name:
            game.apk_name = game.apk_name.replace('http://apk.pujia8.com', 'https://gamefiles.b0.upaiyun.com')
            p = True
        if game.obb_name and 'http://apk.pujia8.com' in game.obb_name:
            game.obb_name = game.obb_name.replace('http://apk.pujia8.com', 'https://gamefiles.b0.upaiyun.com')
            p = True
        if p:
            game.save()
fix_dl2.short_description = u'修正载点2'

def fix_qiuhanhua_num(modeladmin, request, queryset):
    for game in queryset:
        game.qiuhanhua_num = game.qiuhanhua.all().count()
        game.save(update_fields = ['qiuhanhua_num'])
fix_qiuhanhua_num.short_description = u'修正求汉化数'

def update_add_time(modeladmin, request, queryset):
    import time
    nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    for game in queryset:
        game.add_time = nowtime
        game.save()
update_add_time.short_description = u'更新添加时间'

def update_tag(modeladmin, request, queryset):
    for game in queryset:
        if u'扑家' in game.team:
            if game.tags:
                game.tags += u' 扑家'
            else:
                game.tags = u'扑家'
            game.save()
update_tag.short_description = u'更新标签'

def update_add_time_down(modeladmin, request, queryset):
    for game in queryset:
        game.add_time = game.publish_time
        game.save()
update_add_time_down.short_description = u'更新添加时间为发布时间'


def update_post(modeladmin, request, queryset):
    for game in queryset:
        game.post = '0'
        game.save()
update_post.short_description = u'标记为不发表'

def update_hot(modeladmin, request, queryset):
    for game in queryset:
        game.hot = '1'
        game.save()
update_hot.short_description = u'标记为热门'

def update_comments_count(modeladmin, request, queryset):
    for game in queryset:
        target = '/library/%d/'%game.id
        game.comments_count = PujiaComment.objects.select_related().filter(target = target).count()
        game.save()
update_comments_count.short_description = u'更新评论数'

def refresh_downlink(modeladmin, request, queryset):
    response = urllib2.urlopen(urllib2.Request(host_api + get_token_api, urllib.urlencode(data))).read()
    token = json.loads(response)['access_token']

    for game in queryset:
        if game.apk_name:
            url = 'https://d.pujia8.com/apk/' + game.apk_name
            data2 = {"token": token, "type": "file", "urls": url}
            urllib2.urlopen(urllib2.Request(host_api + refresh_api, urllib.urlencode(data2)))
        if game.obb_name:
            url = 'https://d.pujia8.com/obb/' + game.obb_name
            data2 = {"token": token, "type": "file", "urls": url}
            urllib2.urlopen(urllib2.Request(host_api + refresh_api, urllib.urlencode(data2)))
refresh_downlink.short_description = u'刷新下载缓存'

def make_dl(modeladmin, request, queryset):
    fn = 'games/apk.txt'
    fn2 = 'games/obb.txt'
    dst = open(fn, 'wb')
    dst2 = open(fn2, 'wb')
    for game in queryset:
        if game.apk_name and 'qiniucdn.com' in game.apk_name:
            dst.write(game.apk_name+'\r\n')
        if game.obb_name and 'qiniucdn.com' in game.obb_name:
            dst2.write(game.obb_name + '\r\n')
    dst.close()
    dst2.close()
make_dl.short_description = u'生成下载列表'

# class GamesForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         self.request = kwargs.pop('request', None)
#         super(GamesForm, self).__init__(*args, **kwargs)
#         print kwargs
#         self.fields["name"].initial = self.request.user.pk

class GamesAdmin(admin.ModelAdmin):
    actions = [update_add_time, update_post, update_hot, update_comments_count, fix_img, refresh_downlink]
    list_display = ['title_cn', 'count', 'qiuhanhua_num', 'package', 'show_ui']
    search_fields = ['title_cn', 'package']
    list_filter = ['platform', 'state', 'language']
    radio_fields = {'post': admin.HORIZONTAL,'hot': admin.HORIZONTAL,'state': admin.HORIZONTAL, 'comment': admin.HORIZONTAL}
    raw_id_fields = ('name', )
    fieldsets = (
        (u'基本信息', {
            'fields': ('title_cn', 'title_src', 'platform', 'language', 'imagefile', 'developer', 'tags', 'game_size',
                       'publish_time', 'download_link', 'content')
        }),
        (u'安卓客户端', {
            'fields': ('package', 'apk_name', 'obb_name', 'versionName', ('network', 'vpn', 'Advertisement', 'google_framework', 'iap', 'hh'), 'introduce')
        }),
        (u'模拟器', {
            'fields': ('emu_game_code', 'emu_game_name')
        }),
        (u'汉化信息', {
            'classes': ('collapse',),
            'fields': ('team', 'level', 'qiuhanhua_num', 'week_qiuhanhua_num', 'publish_url', )
        }),
        (u'相关链接', {
            'classes': ('collapse',),
            'fields': ('review_id', 'gospel_id')
        }),
        (u'高级设置', {
            'classes': ('collapse',),
            'fields': ('post', 'hot', 'state', 'comment', 'name', 'lianyun', 'h5game')
        }),
    )
    def show_ui(self, obj):
        return '<a target="_blank" href="%s">查看</a>'%reverse("game_detail", args=[obj.pk])
    show_ui.allow_tags = True
    show_ui.short_description = u'在前台查看'

class PlatformAdmin(admin.ModelAdmin):
    list_display = ['id', 'platform']

class QiuHanHuaAdmin(admin.ModelAdmin):
    list_display = ['id', 'game', 'user']
    search_fields = ['game__title_cn']

class GameScoreAdmin(admin.ModelAdmin):
    list_display = ['id', 'game', 'pp', 'user']

class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'post']
    raw_id_fields = ('name', )

admin.site.register(Games,GamesAdmin)
admin.site.register(Platform,PlatformAdmin)
admin.site.register(QiuHanHua,QiuHanHuaAdmin)
admin.site.register(GameScore,GameScoreAdmin)
admin.site.register(Collection,CollectionAdmin)
