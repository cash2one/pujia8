# -*- coding:utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

class Gifts(models.Model):
    subject = models.CharField('主题', max_length=999)
    icon = models.ImageField('图标',upload_to = 'upload')
    url = models.CharField('链接',max_length=300,default='/')
    description = models.TextField('说明', default='')
    rate = models.IntegerField('概率', default=100)
    pp = models.IntegerField('所需PP', default=0)
    file = models.FileField('文件',upload_to = 'cdkeys',blank=True,null=True)
    add_time = models.DateTimeField('时间',auto_now_add=True)
    days = models.IntegerField('连签天数', default=7)
    times = models.IntegerField('次数', default=0)
    post = models.BooleanField('发布', default=True)
    suggest = models.BooleanField('推荐', default=False)
    class Meta:
        verbose_name = '礼包'
        verbose_name_plural = '礼包'
    def __unicode__(self):
        return self.subject

class Cdkeys_Table(models.Model):
    gifts = models.ForeignKey(Gifts, verbose_name='礼包', related_name='cdkeys')
    cdkey = models.CharField('兑换码',max_length=300,default='')
    class Meta:
        verbose_name = '兑换码'
        verbose_name_plural = '兑换码'
    def __unicode__(self):
        return self.cdkey

class Cdkeys_Record(models.Model):
    gifts = models.ForeignKey(Gifts, verbose_name='礼包')
    user = models.ForeignKey(User,verbose_name='兑换者')
    cdkey = models.CharField('兑换码',max_length=300,default='')
    class Meta:
        verbose_name = '兑换记录'
        verbose_name_plural = '兑换记录'
