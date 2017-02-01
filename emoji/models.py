# -*- coding:utf-8 -*-

from django.db import models

class Emoji(models.Model):
    name = models.CharField('表情包', max_length=50)

    class Meta:
        verbose_name = '表情包'
        verbose_name_plural = '表情包'

    def __unicode__(self):
        return self.name

class Emoji_img(models.Model):
    emoji = models.ForeignKey(Emoji, verbose_name=u'表情包')
    description = models.CharField('表情描述', max_length=50)
    img = models.ImageField('表情图片', upload_to = 'emoji')

    class Meta:
        verbose_name = '表情图片'
        verbose_name_plural = '表情图片'

    def __unicode__(self):
        return self.img
