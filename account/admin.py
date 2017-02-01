# -*- coding:utf-8 -*-

from models import Profile, Bonus
from django.contrib import admin
from django.contrib.auth.models import User
from gallery.models import Gallery
from pujia_comments.models import PujiaComment

def rm_avatar(modeladmin, request, queryset):
    for pf in queryset:
        pf.avatar = ''
        pf.save()
rm_avatar.short_description = u'清空头像'

def bat_checkin(modeladmin, request, queryset):
    for pf in queryset:
        if str(pf.check_in_data) != '2015-08-13':
            pf.check_in_data = '2015-08-13'
            pf.check_in += 1
            pf.check_in_total += 1
            pf.save()
bat_checkin.short_description = u'批量签到'

def update_gallery(modeladmin, request, queryset):
    for pf in queryset:
        if pf.background:
            g = Gallery(user = pf.user, imagefile = pf.background)
            g.save()
update_gallery.short_description = u'保存壁纸'

def update_pp(modeladmin, request, queryset):
    for pf in queryset:
        if pf.pp > 0:
            continue
        u = pf.user
        t = u.topic_set.all().count()
        p = u.post_set.all().count()
        g = u.games_set.all().count()
        from django.contrib.comments.models import Comment
        c = Comment.objects.select_related().filter(user = u).count()
        pf.pp = t*10 + p*2 + g*20 + c*2 + 100
        pf.save()
update_pp.short_description = u'更新PP'

def update_super_comment(modeladmin, request, queryset):
    for pf in queryset:
        if 400000 <= pf.id <= 500000:
            num = PujiaComment.objects.select_related().filter(name = pf.user, hot = True).count()
            pf.super_comment = num
            pf.save()
update_super_comment.short_description = u'更新超言弹数'

class ProfileAdmin(admin.ModelAdmin):
    actions = [update_gallery, bat_checkin, update_super_comment]
    list_display = ['id', 'user', 'check_in', 'check_in_total', 'super_comment', 'avatar', 'pp', 'gp', 'today_score_times']
    list_display_links = ['user']
    search_fields = ['user__username']
    raw_id_fields = ('user',)

class BonusAdmin(admin.ModelAdmin):
    list_display = ['user', 'pp', 'gp', 'description']
    search_fields = ['user__username']
    raw_id_fields = ('user',)

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Bonus, BonusAdmin)