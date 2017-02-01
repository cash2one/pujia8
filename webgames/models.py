# -*- coding:utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

class Puji(models.Model):
    user = models.ForeignKey(User,verbose_name='兑换者', default=u'1')
    add_time = models.DateTimeField('兑换时间',auto_now_add=True)
    serverid = models.IntegerField('服务区',default = 1)
    class Meta:
        verbose_name = '扑姬兑换'
        verbose_name_plural = '扑姬兑换'

class Pay_PP(models.Model):
    user = models.ForeignKey(User,verbose_name='兑换者', default=u'1')
    serverid = models.IntegerField('服务区', default = 1)
    game = models.CharField('游戏', max_length=30)
    value = models.IntegerField('已返利PP数', default = 0)
    class Meta:
        verbose_name = '返利PP'
        verbose_name_plural = '返利PP'

