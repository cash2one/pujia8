#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from models import Category, Forum, TopicType, Topic, \
        Post, LBForumUserProfile, gen_last_post_info, Seed, Score

admin.site.register(Category)

class SeedAdmin(admin.ModelAdmin):
    raw_id_fields = ('topic', 'seed_by',)
admin.site.register(Seed, SeedAdmin)

class ScoreAdmin(admin.ModelAdmin):
    raw_id_fields = ('post', 'score_by',)
    search_fields = ('score_by__username', )
    list_display = ('score_by', 'pp')
admin.site.register(Score, ScoreAdmin)

def update_forum_state_info(modeladmin, request, queryset):
    for forum in queryset:
        forum.update_state_info()
update_forum_state_info.short_description = _("Update forum state info")

class ForumAdmin(admin.ModelAdmin):
    list_display        = ('name', 'slug', 'category', 'num_topics', \
            'num_posts', )
    list_filter         = ('category',)
    actions = [update_forum_state_info]

admin.site.register(Forum, ForumAdmin)

class TopicTypeAdmin(admin.ModelAdmin):
    list_display        = ('forum', 'name', 'slug', 'description', )
    list_filter         = ('forum',)

admin.site.register(TopicType, TopicTypeAdmin)

class PostInline(admin.TabularInline):
    model = Post

def update_topic_state_info(modeladmin, request, queryset):
    for topic in queryset:
        topic.update_state_info()
update_topic_state_info.short_description = _("Update topic state info")

def update_topic_attr_as_not(modeladmin, request, queryset, attr):
    for topic in queryset:
        if attr == 'sticky':
            topic.sticky = not topic.sticky
        elif attr == 'close':
            topic.closed = not topic.closed
        elif attr == 'hide':
            topic.hidden = not topic.hidden
        topic.save()

def sticky_unsticky_topic(modeladmin, request, queryset):
    update_topic_attr_as_not(modeladmin, request, queryset, 'sticky')
sticky_unsticky_topic.short_description = _("sticky/unsticky topics")

def close_unclose_topic(modeladmin, request, queryset):
    update_topic_attr_as_not(modeladmin, request, queryset, 'close')
close_unclose_topic.short_description = _("close/unclose topics")

def hide_unhide_topic(modeladmin, request, queryset):
    update_topic_attr_as_not(modeladmin, request, queryset, 'hide')
hide_unhide_topic.short_description = _("hide/unhide topics")

def fix_pujiahh(modeladmin, request, queryset):
    for post in queryset:
        if 'pujiahh.com' not in post.message:
            continue
        post.message = post.message.replace('pujiahh.com', 'pujia8.com')
        post.save()
fix_pujiahh.short_description = u'修正域名信息'

class TopicAdmin(admin.ModelAdmin):
    list_display        = ('subject', 'forum', 'topic_type', 'posted_by', 'sticky', 'closed',
            'hidden', 'level', 'num_views', 'num_replies', 'created_on', 'updated_on', )
    list_filter         = ('forum', 'sticky', 'closed', 'hidden', 'level')
    search_fields       = ('subject', 'posted_by__username', )
    raw_id_fields = ('posted_by', 'post',)
    #inlines             = (PostInline, )
    actions = [update_topic_state_info, sticky_unsticky_topic, close_unclose_topic,
            hide_unhide_topic]

admin.site.register(Topic, TopicAdmin)

class PostAdmin(admin.ModelAdmin):
    list_display        = ('message',)
    raw_id_fields = ('posted_by', 'topic',)
    search_fields       = ('topic__subject', 'posted_by__username', 'message', )
    actions = [fix_pujiahh, ]

admin.site.register(Post, PostAdmin)

class LBForumUserProfileAdmin(admin.ModelAdmin):
    list_display        = ('user', 'userrank', 'last_activity', 'last_posttime', )
    search_fields       = ('user__username', 'userrank', )

admin.site.register(LBForumUserProfile, LBForumUserProfileAdmin)
