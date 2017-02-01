# -*- coding:utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from tagging.fields import TagField

class GalleryApp(models.Model):
    title = models.CharField('主题', max_length=300, blank=True, null=True)
    tags = TagField('标签', max_length=30)
    add_time = models.DateTimeField('添加时间', auto_now_add=True)
    num_likes = models.IntegerField('喜欢数', default=0)
    num_views = models.IntegerField('查看数', default=0)
    user = models.ForeignKey(User, verbose_name='上传者', default=u'41')
    class Meta:
        verbose_name = '图库App'
        verbose_name_plural = '图库App'
    def __unicode__(self):
        return self.title

class Image(models.Model):
    gallery = models.ForeignKey(GalleryApp, verbose_name='图库', related_name='imgs')
    imagefile = models.ImageField('图片',upload_to = 'gallery')
    class Meta:
        verbose_name = '图片'
        verbose_name_plural = '图片'
