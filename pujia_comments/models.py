#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.shortcuts import get_object_or_404
from games.models import Games
from flow.models import Flow

class PujiaComment(models.Model):
    name = models.ForeignKey(User, verbose_name = '评论人')
    date = models.DateTimeField('添加时间', auto_now_add=True)
    path = models.CommaSeparatedIntegerField('路径', max_length = 9, blank = True)
    depth = models.PositiveSmallIntegerField('深度', default=0)
    target = models.CharField('对象', max_length = 100)
    content = models.TextField('内容')
    hot = models.BooleanField('热门', default = False)
    positive = models.IntegerField('支持', default = 0)

    def __unicode__(self):
        return self.content

    class Meta:
        verbose_name = '言弹'
        verbose_name_plural = '言弹'

class CommentPositive(models.Model):
    user = models.ForeignKey(User, verbose_name = '支持者')
    comment = models.ForeignKey(PujiaComment, verbose_name = '目标评论')

    class Meta:
        verbose_name = '赞TA'
        verbose_name_plural = '赞TA'

def comment_update(sender, instance, created, **kwargs):
    if created:
        if 'library' in instance.target:
            try:
                gid = int(instance.target.split('/')[2])
                game = Games.objects.select_related().get(id = gid)
            except:
                package = instance.target.split('/')[2]
                game = Games.objects.select_related().get(package = package)
            game.comments_count += 1
            game.save()
        if 'news' in instance.target:
            nid = int(instance.target.split('/')[2])
            flow = Flow.objects.select_related().get(id = nid)
            flow.comment += 1
            flow.save()

def comment_del(sender, instance, **kwargs):
    if 'library' in instance.target:
        try:
            gid = int(instance.target.split('/')[2])
            game = Games.objects.select_related().get(id=gid)
        except:
            package = instance.target.split('/')[2]
            game = Games.objects.select_related().get(package=package)
        game.comments_count -= 1
        game.save()
    if 'news' in instance.target:
        nid = int(instance.target.split('/')[2])
        flow = Flow.objects.select_related().get(id=nid)
        flow.comment -= 1
        flow.save()

def set_positive(sender, instance, created, **kwargs):
    if created:
        comment = get_object_or_404(PujiaComment, id = instance.comment_id)
        comment.positive += 1
        if comment.positive == 5:
            comment.hot = True
            u = comment.name.get_profile()
            u.pp += 20
            u.super_comment += 1
            u.save(update_fields = ['pp', 'super_comment'])
        comment.save()

post_save.connect(comment_update, sender = PujiaComment, dispatch_uid="pujia_comments.models")
post_delete.connect(comment_del, sender = PujiaComment, dispatch_uid="pujia_comments.models")
post_save.connect(set_positive, sender = CommentPositive, dispatch_uid="pujia_comments.models")

