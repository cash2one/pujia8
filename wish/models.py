# -*- coding:utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from games.models import Platform
from redactor.fields import RedactorField

class Wish(models.Model):
    title = models.CharField('游戏名称',max_length=100)
    slug = models.SlugField('URL',max_length = 100)
    platform = models.ManyToManyField(Platform, verbose_name='游戏平台')
    gamepack = models.ImageField('游戏封面',upload_to = 'screenshots')
    add_time = models.DateTimeField('添加时间',auto_now_add=True)
    deadline = models.DateField('截止日期')
    team = models.CharField('立项组织',max_length=100)
    game_type = models.CharField('游戏类型',max_length=30)
    content = RedactorField('许愿介绍',max_length=5000)
    pp_need = models.IntegerField('所需PP',default=100000)
    pp_now = models.IntegerField('当前PP',default=0)
    user = models.ForeignKey(User,verbose_name='发起人')
    fin = models.BooleanField('许愿成功', default=False)

    class Meta:
        verbose_name = '许愿池'
        verbose_name_plural = '许愿池'

    def __unicode__(self):
        return self.title

class WishRecord(models.Model):
    tar_wish = models.ForeignKey(Wish,verbose_name='许愿对象')
    user = models.ForeignKey(User,verbose_name='许愿者')
    pp_wish = models.IntegerField('许愿PP',default=0)

    class Meta:
        verbose_name = '许愿记录'
        verbose_name_plural = '许愿记录'

    def __unicode__(self):
        return self.user.username
