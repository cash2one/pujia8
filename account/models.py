# -*- coding:utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class Profile(models.Model):
    STATE_CHOICES = (
        (u'2',u'版主'),
        (u'1',u'黑名单'),
        (u'0',u'普通用户'),
    )
    user = models.ForeignKey(User, verbose_name='用户')
    avatar = models.ImageField('头像',upload_to = 'avatars', blank=True)
    background = models.ImageField('背景',upload_to = 'background', blank=True)
    introduce = models.TextField('个人介绍',max_length=80, blank=True, null = True)
    count = models.IntegerField('总翻译数', default=0)
    today = models.DateField('今天日期', blank=True)
    todaycount = models.IntegerField('今日翻译数', default=0)
    notification = models.IntegerField('提醒', default=0)
    verify = models.CharField('认证',max_length=50, blank=True, null = True)
    pp = models.IntegerField('PP', default=10)
    gp = models.IntegerField('GP', default=0)
    check_in = models.IntegerField('连续签到数', default=0)
    check_in_total = models.IntegerField('总签到数', default=0)
    check_in_data = models.DateField('签到日期', blank=True)
    today_score_times = models.IntegerField('今日宠幸数', default=0)
    super_comment = models.IntegerField('超言弹数', default=0)
    female = models.BooleanField('女生', default=False)
    state = models.CharField('用户状态',max_length=2, choices=STATE_CHOICES, default=u'0')
    app_sync = models.CharField('APP同步',max_length=5000, blank=True)  # pickle obj

    class Meta:
        verbose_name = '个人资料'
        verbose_name_plural = '个人资料'

    def __unicode__(self):
        return self.user.username

class Bonus(models.Model):
    user = models.ForeignKey(User, verbose_name='用户')
    description = models.CharField('奖励说明', max_length=500)
    gp = models.IntegerField('GP', default=0)
    pp = models.IntegerField('PP', default=0)
    add_time = models.DateTimeField('时间', auto_now_add=True)

    class Meta:
        verbose_name = '奖励'
        verbose_name_plural = '奖励'

    def __unicode__(self):
        return self.user.username

def post_bonus(sender, instance, created, **kwargs):
    if created:
        user_profile = instance.user.get_profile()
        user_profile.pp += instance.pp
        user_profile.gp += instance.gp
        user_profile.save()

post_save.connect(post_bonus, sender = Bonus, dispatch_uid="account.models")