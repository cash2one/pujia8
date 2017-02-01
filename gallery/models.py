# -*- coding:utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

class Gallery(models.Model):
    user = models.ForeignKey(User,verbose_name='上传者', default=u'1')
    imagefile = models.ImageField('图片',upload_to = 'background')
    add_time = models.DateTimeField('添加时间',auto_now_add=True)
    count = models.IntegerField('喜欢数',default=0)
    class Meta:
        verbose_name = '壁纸'
        verbose_name_plural = '壁纸'
