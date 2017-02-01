# -*- coding:utf-8 -*-

from models import Link
from django.contrib import admin

class LinkAdmin(admin.ModelAdmin):
    list_display = ['id', 'content', 'todaycount', 'monthcount', 'count']
    list_display_links = ['content']
    search_fields = ['content']

admin.site.register(Link, LinkAdmin)
