# -*- coding:utf-8 -*-

from django.db import models

class Adm(models.Model):
    position = models.CharField('广告位置',max_length=50)
    slug = models.SlugField('广告代码',max_length = 100)
    size = models.CharField('物料尺寸',max_length=50)

    class Meta:
        verbose_name = '广告位'
        verbose_name_plural = '广告位'

    def __unicode__(self):
        return self.position

class Material(models.Model):
    title = models.CharField('广告名称',max_length=50)
    adm = models.ForeignKey(Adm, verbose_name='广告位', related_name='ad')
    weight = models.IntegerField('权重', default=5)
    imagefile = models.ImageField('广告图片',upload_to = 'material')
    link = models.CharField('目标网址',max_length=500)
    post = models.BooleanField('是否投放', default=True)

    class Meta:
        verbose_name = '广告物料'
        verbose_name_plural = '广告物料'

    def __unicode__(self):
        return self.title

class Game_ads(models.Model):
    AD_CHOICES = (
        (0, u'不显示'),
        (1, u'巴依'),
        (2, u'联想'),
        (3, u'卓易'),
        (4, u'Adview'),
        (5, u'Uniplay'),
        (6, u'adwo'),
    )
    CHANNEL_CHOICES = (
        (u'pj',u'扑家'),
        (u'hack',u'联想'),
        (u'wdj',u'豌豆荚'),
        (u'wdjlx',u'豌豆荚2'),
        (u'xx',u'叉叉助手'),
        (u'dl',u'当乐'),
        (u'qh',u'360'),
        (u'zy',u'卓易'),
        (u'mmy',u'木蚂蚁'),
        (u'yyb',u'应用宝'),
        (u'hw',u'华为'),
        (u'mz',u'魅族'),
        (u'xm',u'小米'),
        (u'az',u'安智'),
    )
    package = models.CharField('包名', max_length=500)
    channel = models.CharField('渠道', max_length=500, choices = CHANNEL_CHOICES, default = u'pj')
    banner = models.IntegerField('横幅',max_length = 10, choices = AD_CHOICES, default = 3)
    inst = models.IntegerField('插屏',max_length = 10, choices = AD_CHOICES, default = 1)
    splash = models.IntegerField('开屏',max_length = 10, choices = AD_CHOICES, default = 1)
    timespan = models.IntegerField('间隔时长(分钟)', max_length = 10, default = 5)
    sms = models.BooleanField('移动SDK', default=True)
    pujiasdk = models.BooleanField('扑家SDK', default=True)
    patch_url = models.CharField('补丁下载', max_length=500, blank=True, null=True)
    adview_key = models.CharField('AdviewKey', max_length=500, blank=True, null=True)
    VersionCode = models.IntegerField('VersionCode', max_length = 10, default = 1, blank=True, null=True)
    add_time = models.DateTimeField('添加时间', auto_now_add=True)

    class Meta:
        verbose_name = '广告配置'
        verbose_name_plural = '广告配置'

    def __unicode__(self):
        return self.package
