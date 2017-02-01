# -*- coding:utf-8 -*-

from models import Wish, WishRecord
from django.contrib import admin

class WishAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'pp_need', 'pp_now']
    search_fields = ['title',]
    list_filter = ['fin']
    raw_id_fields = ('user', )
    list_display_links = ['title']
    fieldsets = (
        (u'基本信息', {
            'fields': ('title', 'slug', 'platform', 'gamepack', 'deadline', 'team', 'game_type', 'content')
        }),
        (u'高级设置', {
            'classes': ('collapse',),
            'fields': ('pp_need', 'user', 'fin')
        }),
        )

class WishRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'tar_wish', 'user', 'pp_wish']
    list_filter = ['tar_wish']
    raw_id_fields = ('user', )

admin.site.register(Wish,WishAdmin)
admin.site.register(WishRecord,WishRecordAdmin)
