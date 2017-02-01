# -*- coding:utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from redactor.fields import RedactorField
from django.db.models.signals import post_save, post_delete
from django.contrib.comments.models import Comment
from tagging.fields import TagField
from PIL import ImageFile, Image
import re, os

class Platform(models.Model):
    platform = models.CharField('游戏平台',max_length=30)
    class Meta:
        verbose_name = '游戏平台'
        verbose_name_plural = '游戏平台'
    def __unicode__(self):
        return self.platform

class Games(models.Model):
    NORMAL_CHOICES = (
        (u'1',u'是'),
        (u'0',u'否'),
    )
    STATE_CHOICES = (
        (u'2',u'汉化中'),
        (u'1',u'已发布'),
        (u'0',u'未发布'),
        )
    LNG_CHOICES = (
        (u'cn',u'中文汉化'),
        (u'en',u'英文'),
        (u'jp',u'日文'),
        )
    CATE_CHOICES = (
        (u'0',u'休闲时间'),
        (u'1',u'跑酷竞速'),
        (u'2',u'宝石消除'),
        (u'3',u'网络游戏'),
        (u'4',u'动作射击'),
        (u'5',u'扑克棋牌'),
        (u'6',u'儿童益智'),
        (u'7',u'塔防守卫'),
        (u'8',u'体育格斗'),
        (u'9',u'角色扮演'),
        (u'10',u'经营策略'),
        )
    title_cn = models.CharField('游戏译名',max_length=30)
    title_src = models.CharField('游戏原名',max_length=30,blank=True,null=True)
    platform = models.ManyToManyField(Platform, verbose_name='游戏平台')
    language = models.CharField('游戏语言',max_length=10, choices=LNG_CHOICES, default=u'cn')

    imagefile = models.ImageField('游戏封面',upload_to = 'screenshots')
    team = models.CharField('汉化小组',max_length=30,blank=True,null=True)
    level = models.CharField('汉化程度',max_length=30,blank=True,null=True)
    publish_time = models.DateField('发布日期',blank=True,null=True)
    add_time = models.DateTimeField('添加时间',auto_now_add=True)
    tags = TagField('类型标签',max_length=30)
    game_size = models.CharField('游戏容量',max_length=30,blank=True,null=True)
    publish_url = models.CharField('发布地址',max_length=300,blank=True,null=True)
    download_link = RedactorField('下载地址',max_length=1000,blank=True,null=True)
    content = RedactorField('汉化信息',max_length=5000,blank=True,null=True)
    count = models.IntegerField('点击数',default=1)
    comments_count = models.IntegerField('评论数',default=0)
    qiuhanhua_num = models.IntegerField('求汉化数',default=0)
    week_qiuhanhua_num = models.IntegerField('每周求汉化数', default=0)

    introduce = models.TextField('游戏介绍',max_length=800,blank=True,null = True)
    package = models.CharField('包名',max_length=300,blank=True,null=True)
    apk_name = models.CharField('apk名称',max_length=300,blank=True,null=True)
    obb_name = models.CharField('obb名称',max_length=300,blank=True,null=True)

    post = models.CharField('发表',max_length=2, choices=NORMAL_CHOICES, default=u'1')
    hot = models.CharField('推荐',max_length=2, choices=NORMAL_CHOICES, default=u'0')
    state = models.CharField('汉化状态',max_length=2, choices=STATE_CHOICES, default=u'1')
    comment = models.CharField('评论',max_length=2, choices=NORMAL_CHOICES, default=u'1')
    name = models.ForeignKey(User,verbose_name='编辑', default=u'3202')
    review_id = models.IntegerField('评测帖ID',blank=True,null=True)
    gospel_id = models.IntegerField('攻略帖ID',blank=True,null=True)
    lianyun = models.BooleanField('联运', default=False)
    h5game = models.BooleanField('H5游戏', default=False)

    #for app
    categoryName = models.CharField('游戏类型',max_length=2, choices=CATE_CHOICES, blank=True,null=True)
    versionCode = models.CharField(max_length=10,blank=True,null=True)
    versionName = models.CharField(max_length=10,blank=True,null=True)
    changelog = models.CharField('更新日志', max_length=100,blank=True,null=True)
    developer = models.CharField('开发者', max_length=100,blank=True,null=True)
    lastFetchTime = models.DateTimeField('更新时间',blank=True,null=True)

    network = models.BooleanField('联网', default=False)
    vpn = models.BooleanField('VPN', default=False)
    Advertisement = models.BooleanField('广告', default=True)
    google_framework = models.BooleanField('谷歌框架', default=False)
    iap = models.BooleanField('内购', default=False)
    hh = models.BooleanField('汉化', default=False)

    emu_game_code = models.CharField('模拟游戏CODE', max_length=100,blank=True,null=True)
    emu_game_name = models.CharField('模拟游戏名称', max_length=300,blank=True,null=True)

    apk_name_wdj = models.CharField('豌豆荚apk名称',max_length=300,blank=True,null=True)
    apk_name_mmy = models.CharField('木蚂蚁apk名称',max_length=300,blank=True,null=True)

    #for joyme
    joyme_content = models.TextField('着迷推荐',max_length=5000,blank=True,null = True)

    #for_chinamobile
    sms = models.BooleanField('移动so', default=False)

    class Meta:
        verbose_name = '游戏库'
        verbose_name_plural = '游戏库'

    def __unicode__(self):
        return self.title_cn

    @models.permalink
    def get_absolute_url(self):
        return 'game_detail', (), {'gid': self.id}

class QiuHanHua(models.Model):
    game = models.ForeignKey(Games, verbose_name='游戏', related_name='qiuhanhua')
    user = models.ForeignKey(User)
    qhh_date = models.DateField('求汉化日期', blank=True, null=True)
    class Meta:
        verbose_name = '求汉化'
        verbose_name_plural = '求汉化'
    def __unicode__(self):
        return self.user.username

class GameScore(models.Model):
    game = models.ForeignKey(Games, verbose_name='游戏', related_name='game_score')
    pp = models.IntegerField(default=0)
    user = models.ForeignKey(User)
    class Meta:
        verbose_name = '宠幸'
        verbose_name_plural = '宠幸'
    def __unicode__(self):
        return self.user.username

class GameCollection(models.Model):
    user = models.ForeignKey(User, verbose_name = u'用户', related_name = 'game_user')
    game = models.ForeignKey(Games, verbose_name = u'游戏')

    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = '收藏'

    def __unicode__(self):
        return self.user.username

class Collection(models.Model):
    title = models.CharField('专题名称',max_length=100)
    description = models.TextField('专题说明',max_length=5000,blank=True,null = True)
    game_id = models.CharField('游戏ID',max_length=100)
    name = models.ForeignKey(User,verbose_name='作者', default=u'3153', related_name = 'collection_user')
    lastFetchTime = models.DateTimeField('更新时间',blank=True,null=True)
    post = models.BooleanField('发表', default=True)
    class Meta:
        verbose_name = '专题'
        verbose_name_plural = '专题'
    def __unicode__(self):
        return self.title

def post_game(sender, instance, created, **kwargs):
    if created:
        u = instance.name.get_profile()
        u.pp += 20
        u.save()
    images_list = re.findall('(/static/[\S]*.[jpg|jpeg|png])', instance.content)
    for img in images_list:
        try:
            fn = os.path.dirname(__file__)[:-6] + img
            im = Image.open(fn)
            width, heigth = im.size
            if width * 16 / heigth <= 9 or heigth > 600:
                im = im.resize((600*width/heigth, 600),  Image.ANTIALIAS)
            elif width > 800:
                im = im.resize((800, 800*heigth/width),  Image.ANTIALIAS)
            im.convert(mode='RGBA').save(fn, quality = 80)
        except:
            pass

def del_game(sender, instance, **kwargs):
    u = instance.name.get_profile()
    u.pp -= 20
    u.save()

post_save.connect(post_game, sender = Games, dispatch_uid="games.models")
post_delete.connect(del_game, sender = Games, dispatch_uid="games.models")
