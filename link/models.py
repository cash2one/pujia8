# -*- coding:utf-8 -*-

from django.db import models

class Link(models.Model):
    content = models.CharField('说明', max_length=300)
    slug = models.SlugField(max_length=110)
    url = models.CharField('链接', max_length=3000)
    todaycount = models.IntegerField('今日点击', default=0)
    monthcount = models.IntegerField('本月点击', default=0)
    count = models.IntegerField('总点击数', default=0)

    class Meta:
        verbose_name = '统计链接'
        verbose_name_plural = '统计链接'

    def __unicode__(self):
        return self.content
