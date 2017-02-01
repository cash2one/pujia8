# -*- coding:utf-8 -*-
from models import GalleryApp, Image
from django.contrib import admin

def fix_tag(modeladmin, request, queryset):
    for gallery in queryset:
        gallery.save()
fix_tag.short_description = u'修正tag22'

class GalleryImageInline(admin.TabularInline):
    model = Image
    extra = 5

class GalleryAppAdmin(admin.ModelAdmin):
    actions = [fix_tag, ]
    inlines = (GalleryImageInline,)
    raw_id_fields = ('user', )
    list_display = ['id', 'title', 'user', 'tags']
    search_fields = ['user__username', 'title']

admin.site.register(GalleryApp, GalleryAppAdmin)
