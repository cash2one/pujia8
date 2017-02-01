# -*- coding:utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

class GameRequest(models.Model):
    CATEGORY_CHOICES = (
        (u'0', u'NDS'),
        (u'1', u'PSP'),
        (u'2', u'WII'),
        (u'3', u'PS2'),
        (u'4', u'GBA'),
        (u'5', u'IPHONE'),
        (u'8', u'ANDROID'),
        (u'6', u'PC'),
        (u'7', u'ETC'),
        )
    title = models.CharField('游戏名称',max_length=100)
    category = models.CharField('游戏平台',max_length=2,choices=CATEGORY_CHOICES,default='0')
    gamepack = models.ImageField('游戏封面',upload_to = 'screenshots')
    publish_time = models.DateField('发售日期')
    add_time = models.DateTimeField('添加时间',auto_now_add=True)
    game_type = models.CharField('游戏类型',max_length=30,blank=True,null=True)
    download_link = models.CharField('下载地址',max_length=300)
    introduce = models.TextField('游戏介绍',max_length=5000)
    caption = models.TextField('请愿说明',max_length=5000)
    ip = models.CharField('IP',max_length=30,blank=True,null=True)
    up = models.IntegerField(default=0)
    down = models.IntegerField(default=0)
    name = models.ForeignKey(User,verbose_name='编辑', default=u'1')

    class Meta:
        verbose_name = '汉化请愿'
        verbose_name_plural = '汉化请愿'

    def __unicode__(self):
        return self.title
