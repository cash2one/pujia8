# -*- coding:utf-8 -*-

from django.db import models, connection
from django.contrib.auth.models import User
from tagging.fields import TagField
from tagging.models import Tag
from redactor.fields import RedactorField
from django.db.models.signals import post_save
import urllib2, StringIO, gzip, re, os
from account.models import *
import tagging, random
from tagging.utils import get_tag_list

class Channel(models.Model):
    name = models.CharField('频道', max_length = 100)
    icon = models.ImageField('icon',upload_to = 'icon', blank=True, null=True)
    color = models.CharField('色调', max_length = 100, blank=True, null=True)
    class Meta:
        verbose_name = '频道'
        verbose_name_plural = '频道'

    def __unicode__(self):
        return self.name

class Column(models.Model):
    channel = models.ManyToManyField(Channel, verbose_name = u'频道', related_name = 'channel_column')
    name = models.CharField('栏目', max_length = 100)
    order = models.IntegerField('排序', default = 0)
    display = models.BooleanField('显示', default = True)
    class Meta:
        verbose_name = '栏目'
        verbose_name_plural = '栏目'

    def __unicode__(self):
        return self.name

class FlowManager(models.Manager):
    def get_intersection(self, user_list, tag_list):
        tags = get_tag_list(tag_list)
        tags_id = [int(tag.pk) for tag in tags]
        tags_id.append(0)
        tags_id.append(0)
        user_list.append(0)
        user_list.append(0)
        query = """
        SELECT DISTINCT flow_flow.id
        FROM flow_flow INNER JOIN tagging_taggeditem ON flow_flow.id = tagging_taggeditem.object_id
        WHERE post = 1 AND (user_id IN %(user_list)s OR tag_id IN %(tag_list)s)""" % {
            'user_list': tuple(user_list),
            'tag_list': tuple(tags_id)
        }

        cursor = connection.cursor()
        cursor.execute(query)
        object_ids = [row[0] for row in cursor.fetchall()]
        return self.model.objects.select_related().filter(pk__in = object_ids)

class Flow(models.Model):
    SHOW_TYPE_CHOICES = (
        (u'0',u'右侧图'),
        (u'1',u'一大图'),
        (u'3',u'三小图'),
        (u'n',u'纯文字'),
    )
    title = models.CharField('标题', max_length = 300)
    channel = models.ManyToManyField(Channel, verbose_name = u'频道', related_name = 'channel')
    column = models.ManyToManyField(Column, verbose_name = u'栏目', related_name = 'column')
    content = RedactorField('内容', max_length = 5000)
    tags = TagField('标签', max_length = 100)
    head_img = models.CharField('头图', max_length = 300, blank=True, null=True)
    url = models.CharField('来源链接', max_length = 800, blank=True, null=True)
    user = models.ForeignKey(User, verbose_name = u'作者', default=u'1')
    show_type = models.CharField('展示类型', max_length = 10, choices = SHOW_TYPE_CHOICES, default = u'0')
    comment = models.IntegerField('评论数',default=0)
    count = models.IntegerField('阅读数',default=0)
    add_time = models.DateTimeField('时间')
    hot = models.BooleanField('热门', default=False)
    sticky = models.BooleanField('置顶', default = False)
    verify = models.BooleanField('审核', default=False)
    post = models.BooleanField('发布', default = True)

    objects = FlowManager()

    class Meta:
        verbose_name = '信息流'
        verbose_name_plural = '信息流'

    def __unicode__(self):
        return self.title

    def save(self, **kwargs):
        if not self.head_img:
            pics_list = re.findall('/static/[a-zA-z0-9/\.]+[jpg|JPG|jpeg|JPEG|png|PNG]', self.content)
            if pics_list:
                self.head_img = random.choice(pics_list)
        super(Flow, self).save(**kwargs)

class Video_info(models.Model):
    flow = models.ForeignKey(Flow, verbose_name = u'信息流')
    cid = models.CharField('cid', max_length = 300, blank=True, null=True) #Bilibili
    cover = models.ImageField('视频封面', upload_to = 'cover')
    duration = models.CharField('视频时长', max_length = 300)
    class Meta:
        verbose_name = '视频信息'
        verbose_name_plural = '视频信息'

    def __unicode__(self):
        return self.flow.title

class Subscription(models.Model):
    src_user = models.ForeignKey(User, verbose_name = u'用户', related_name = 'src_user')
    desc_user = models.ForeignKey(User, verbose_name = u'被订阅者', related_name = 'desc_user')

    class Meta:
        verbose_name = '订阅用户'
        verbose_name_plural = '订阅用户'

    def __unicode__(self):
        return self.src_user.username

class Subscription_Tag(models.Model):
    user = models.ForeignKey(User, verbose_name = u'用户', related_name = 'subs_tag_user')
    tag = models.ForeignKey(Tag, verbose_name = u'标签', related_name = 'subs_tag')

    class Meta:
        verbose_name = '订阅标签'
        verbose_name_plural = '订阅标签'

    def __unicode__(self):
        return self.user.username

class Collection(models.Model):
    user = models.ForeignKey(User, verbose_name = u'用户', related_name = 'flow_user')
    flow = models.ForeignKey(Flow, verbose_name = u'信息')

    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = '收藏'

    def __unicode__(self):
        return self.user.username

class Hot_tag(models.Model):
    src = models.CharField('关键字', max_length = 100)
    tag = models.CharField('标签', max_length = 100)
    class Meta:
        verbose_name = '关键字'
        verbose_name_plural = '关键字'

    def __unicode__(self):
        return self.tag

def BiliBili(url):
    compresseddata = urllib2.urlopen(url).read()
    data = gzip.GzipFile(fileobj = StringIO.StringIO(compresseddata)).read()
    cid = re.search('cid=\d+', data).group(0)[4:]
    url = url.replace('video', 'mobile/video')[:-1] + '.html'
    data = urllib2.urlopen(url).read()
    cover_pic = re.search('pics: \'[a-zA-z]+://[^\s]*', data).group(0)[7:-2]
    duration = re.search('duration: \'[0-9:]+', data).group(0)[11:]
    return {'cid': cid, 'cover_pic': cover_pic, 'duration': duration}

def update_flow(sender, instance, created, **kwargs):
    if created:
        if instance.url and u'bilibili.com' in instance.url:
            try:
                video_info = Video_info.objects.select_related().filter(flow_id = instance.id)
                if not video_info.exists():
                    bilibili = BiliBili(instance.url)
                    name = 'cover/' + os.path.basename(bilibili['cover_pic'])
                    pic_dat = urllib2.urlopen(bilibili['cover_pic']).read()
                    fn = os.path.dirname(__file__)[:-4] + 'static/' + name
                    dst = open(fn, 'wb')
                    dst.write(pic_dat)
                    dst.close()
                    u = Video_info(flow = instance, cid = bilibili['cid'], cover = name, duration = bilibili['duration'])
                    u.save()
            except:
                pass
        if not Profile.objects.select_related().filter(user = instance.user).exists():
            profile = Profile(user = instance.user)
            profile.save()

post_save.connect(update_flow, sender = Flow)
tagging.register(Flow, tag_descriptor_attr='flow_tags')
