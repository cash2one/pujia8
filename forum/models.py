#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from base64 import b64encode, b64decode
import pickle

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete, pre_delete
from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length = 100)
    description = models.TextField(default = '')
    ordering = models.PositiveIntegerField(default = 1)
    created_on = models.DateTimeField(auto_now_add = True)
    updated_on = models.DateTimeField(blank = True, null = True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ('-ordering', 'created_on')

    def __unicode__(self):
        return self.name

class Forum(models.Model):
    name = models.CharField(max_length = 100)
    slug = models.SlugField(max_length = 110)
    description = models.TextField(default = '', blank = True, null = True)
    ordering = models.PositiveIntegerField(default = 1)
    category = models.ForeignKey(Category)
    created_on = models.DateTimeField(auto_now_add = True)
    updated_on = models.DateTimeField(blank = True, null = True)
    num_topics = models.IntegerField(default = 0)
    num_posts = models.IntegerField(default = 0)
    pp_topic = models.IntegerField(default = 10)
    pp_post = models.IntegerField(default = 2)
    last_post = models.CharField(max_length = 255, blank = True)#pickle obj
    show_in_index = models.BooleanField('首页显示', default=True)
    show_in_ui = models.BooleanField('前端显示', default=True)

    class Meta:
        verbose_name = _("Forum")
        verbose_name_plural = _("Forums")
        ordering = ('ordering','-created_on')

    def _count_nums_topic(self):
        return self.topics.all().count()

    def _count_nums_post(self):
        return self.topics.all().aggregate(Sum('num_replies'))['num_replies__sum'] or 0

    def get_last_post(self):
        if not self.last_post:
            return {}
        return pickle.loads(b64decode(self.last_post))

    @models.permalink
    def get_absolute_url(self):
        return ('lbforum_forum', (), {'forum_slug': self.slug})

    def __unicode__(self):
        return self.name

    def update_state_info(self, commit=True):
        self.num_topics = self._count_nums_topic()
        self.num_posts = self._count_nums_post()
        if self.num_topics:
            last_post = Post.objects.all().filter(topic__forum=self).order_by('-created_on')[0]
            self.last_post = gen_last_post_info(last_post)
        else:
            self.last_post = ''
        if commit:
            self.save()

class TopicType(models.Model):
    forum = models.ForeignKey(Forum, verbose_name=_('Forum'))
    name = models.CharField(max_length = 100)
    slug = models.SlugField(max_length = 100)
    description = models.TextField(blank=True, default = '')

    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = '主题类别'
        verbose_name_plural = '主题类别'

class TopicManager(models.Manager):
    def get_query_set(self):
        return super(TopicManager, self).get_query_set().filter(hidden = False)

LEVEL_CHOICES = (
        (30, _('Default')),
        (60, _('Distillate')),
        )

class Topic(models.Model):
    forum = models.ForeignKey(Forum, verbose_name=_('Forum'), related_name='topics')
    topic_type = models.ForeignKey(TopicType, verbose_name=_('Topic Type'),
            blank=True, null=True)
    posted_by = models.ForeignKey(User)

    #TODO ADD TOPIC POST.
    post = models.ForeignKey('Post', verbose_name=_('Post'), related_name='topics_',
            blank=True, null=True)
    subject = models.CharField(max_length=999)
    num_views = models.IntegerField(default=0)
    num_seeds = models.IntegerField(default=0)
    num_replies = models.PositiveSmallIntegerField(default=0)#posts...
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(blank=True, null=True)
    last_reply_on = models.DateTimeField(auto_now_add=True)
    last_post = models.CharField(max_length=255, blank=True)#pickle obj

    #Moderation features
    closed = models.BooleanField(default=False)
    sticky = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)
    level = models.SmallIntegerField(choices=LEVEL_CHOICES, default=30)

    objects = TopicManager()

    class Meta:
        ordering = ('-last_reply_on',)#'-sticky'
        get_latest_by = ('created_on')
        verbose_name = _("Topic")
        verbose_name_plural = _("Topics")

    def __unicode__(self):
        return self.subject

    def count_nums_replies(self):
        return self.posts.all().count()

    @models.permalink
    def get_absolute_url(self):
        return ('lbforum_topic', (), {'topic_id': self.id})

    def get_last_post(self):
        if not self.last_post:
            return {}
        return pickle.loads(b64decode(self.last_post))

    def update_state_info(self, commit=True):
        self.num_replies = self.count_nums_replies()
        last_post = self.posts.order_by('-created_on')[0]
        self.last_post = gen_last_post_info(last_post)
        self.save()
        if commit:
            self.save()

class Seed(models.Model):
    topic = models.ForeignKey(Topic, verbose_name=_('Topic'), related_name='seed')
    seed_by = models.ForeignKey(User)
    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = '收藏'
    def __unicode__(self):
        return self.seed_by.username

# Create Replies for a topic
class Post(models.Model):#can't edit...
    topic = models.ForeignKey(Topic, verbose_name=_('Topic'), related_name='posts')
    posted_by = models.ForeignKey(User)
    poster_ip = models.IPAddressField()
    topic_post = models.BooleanField(default=False)
    message = models.TextField()

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(blank = True, null = True)
    edited_by = models.CharField(max_length = 255, blank=True)#user name
    secret = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        ordering = ('-created_on',)
        get_latest_by = ('created_on', )

    def __unicode__(self):
        return self.message[:80]

    def subject(self):
        if self.topic_post:
            return _('Topic: %s') % self.topic.subject
        return _('Re: %s') % self.topic.subject

    @models.permalink
    def get_absolute_url(self):
        return ('lbforum_post', (), { 'post_id': self.pk })

    def get_absolute_url_ext(self):
        topic = self.topic
        post_idx = topic.posts.filter(created_on__lte=self.created_on).count() - 1
        if post_idx == 0:
            page = 1
        elif post_idx % settings.CTX_CONFIG['TOPIC_PAGE_SIZE'] == 0:
            page = post_idx / settings.CTX_CONFIG['TOPIC_PAGE_SIZE']
        else:
            page = post_idx / settings.CTX_CONFIG['TOPIC_PAGE_SIZE'] + 1
        return '%s?page=%s#p%s' % (topic.get_absolute_url(), page, self.pk)

class Score(models.Model):
    post = models.ForeignKey(Post, verbose_name=_('Post'), related_name='score')
    pp = models.IntegerField(default=0)
    score_by = models.ForeignKey(User)
    class Meta:
        verbose_name = '宠幸'
        verbose_name_plural = '宠幸'
    def __unicode__(self):
        return self.score_by.username

class LBForumUserProfile(models.Model):
    user = models.OneToOneField(User, related_name='lbforum_profile', verbose_name=_('User'))
    last_activity = models.DateTimeField(auto_now_add=True)
    userrank = models.CharField(max_length=30,default="Junior Member")
    last_posttime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.user.username

    def get_total_posts(self):
        return self.user.post_set.count()

    def get_absolute_url(self):
        return self.user.get_absolute_url()

    class Meta:
        verbose_name = '会员资料'
        verbose_name_plural = '会员资料'

#### smoe function ###

#### do smoe connect ###
def gen_last_post_info(post):
    last_post = {'posted_by': post.posted_by.username, 'update': post.created_on}
    return b64encode(pickle.dumps(last_post, pickle.HIGHEST_PROTOCOL))

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        print instance
        LBForumUserProfile.objects.create(user=instance)

def update_topic_on_post(sender, instance, created, **kwargs):
    if created:
        t = instance.topic
        t.last_post = gen_last_post_info(instance)
        t.last_reply_on = instance.created_on
        t.num_replies += 1
        t.save()
        u = instance.posted_by.get_profile()
        u.pp += t.forum.pp_post
        u.save()

def update_forum_on_post(sender, instance, created, **kwargs):
    if created:
        instance.topic.forum.last_post = gen_last_post_info(instance)
        instance.topic.forum.num_posts += 1
        instance.topic.forum.save()

def update_forum_on_topic(sender, instance, created, **kwargs):
    if created:
        instance.forum.num_topics += 1
        instance.forum.save()
        u = instance.posted_by.get_profile()
        u.pp += (instance.forum.pp_topic - instance.forum.pp_post)
        u.save()

def update_user_last_activity(sender, instance, created, **kwargs):
    if instance.user:
        p, created = LBForumUserProfile.objects.get_or_create(user=instance.user)
        p.last_activity = instance.updated_on
        p.save()

def del_topic(sender, instance, **kwargs):
    u = instance.posted_by.get_profile()
    u.pp -= (instance.forum.pp_topic - instance.forum.pp_post)
    u.save()

def del_post(sender, instance, **kwargs):
    u = instance.posted_by.get_profile()
    u.pp -= instance.topic.forum.pp_post
    u.save()

def del_score(sender, instance, **kwargs):
    post = Post.objects.select_related().get(id = instance.post_id)
    u = post.posted_by.get_profile()
    u.pp -= instance.pp
    u.save()

#post_save.connect(create_user_profile, sender = User)
post_save.connect(update_topic_on_post, sender = Post, dispatch_uid="forum.models")
post_save.connect(update_forum_on_post, sender = Post, dispatch_uid="forum.models")
post_save.connect(update_forum_on_topic, sender = Topic, dispatch_uid="forum.models")
pre_delete.connect(del_topic, sender = Topic, dispatch_uid="forum.models")
pre_delete.connect(del_post, sender = Post, dispatch_uid="forum.models")
pre_delete.connect(del_score, sender = Score, dispatch_uid="forum.models")
