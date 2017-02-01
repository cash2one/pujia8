# -*- coding:utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from redactor.fields import RedactorField

class Articles(models.Model):
    SUBJECT_CHOICES=(
        (u'0',u'汉化资讯'),
        (u'1',u'汉化交流'),
        (u'2',u'跳转链接'),
    )
    CATEGORY_CHOICES = (
        (u'0', u'NDS'),
        (u'1', u'PSP'),
        (u'2', u'WII'),
        (u'3', u'PS2'),
        (u'4', u'GBA'),
        (u'5', u'IOS'),
        (u'6', u'PC'),
        (u'7', u'ANDROID'),
        (u'99', u'ETC'),
    )
    CATEGORY2_CHOICES = (
        (u'0', u'汉化教程'),
        (u'1', u'汉化研究'),
        (u'2', u'汉化测试'),
        (u'3', u'汉化咨询'),
        (u'4', u'破解求助'),
        (u'5', u'BUG回收'),
        (u'6', u'游戏讨论'),
        (u'7', u'资源分享'),
        )
    STATE_CHOICES = (
        (u'1',u'是'),
        (u'0',u'否'),
    )
    HTML_CHOICES = (
        (u'1',u'不显示'),
        (u'0',u'显示'),
        )
    SOURCE_CHOICES = (
        (u'1',u'原创'),
        (u'0',u'转载'),
    )
    title = models.CharField('标题',max_length=50)
    subject = models.CharField('栏目',max_length=2, choices=SUBJECT_CHOICES, default=u'0')
    name = models.ForeignKey(User,verbose_name='编辑', default=u'1')
    category = models.CharField('平台',max_length=2, choices=CATEGORY_CHOICES, default=u'0')
    category2 = models.CharField('分类',max_length=2, choices=CATEGORY2_CHOICES, default=u'0')
    source = models.CharField('来源',max_length=2, choices=SOURCE_CHOICES, default=u'0')
    sourceurl = models.CharField('来自',max_length=300,blank=True,null=True)
    team = models.CharField('组织',max_length=30,blank=True,null=True)
    label = models.CharField('标签',max_length=30,blank=True,null=True)
    content = RedactorField('内容',max_length=5000)
    time = models.DateTimeField('时间',auto_now_add=True)
    count = models.IntegerField('点击数',default=1)

    post = models.CharField('发表',max_length=2, choices=STATE_CHOICES, default=u'1')
    hot = models.CharField('推荐',max_length=2, choices=STATE_CHOICES, default=u'0')
    html = models.CharField('显示到汉化情报',max_length=2, choices=HTML_CHOICES, default=u'1')
    
    class Meta:
        verbose_name = '汉化文章'
        verbose_name_plural = '汉化文章'

    def __unicode__(self):
        return self.title


