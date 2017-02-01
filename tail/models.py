# -*- coding:utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

class Tail(models.Model):
    user = models.ForeignKey(User,verbose_name='作者', related_name='user',default=u'1')
    add_time = models.DateTimeField('添加时间',auto_now_add=True)
    content = models.TextField('内容', max_length=140)
    tar_user = models.ForeignKey(User,verbose_name='定向目标',related_name='tar_user',blank=True,null=True)
    tar_time = models.DateField('定向时间',blank=True,null=True)

    def __unicode__(self):
        return self.content

    class Meta:
        verbose_name = '小尾巴'
        verbose_name_plural = '小尾巴'
