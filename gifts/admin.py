from models import Gifts, Cdkeys_Table, Cdkeys_Record
from django.contrib import admin
import os, codecs

def import_cdkeys(modeladmin, request, queryset):
    for gifts in queryset:
        fn = os.path.dirname(__file__)[:-6] + gifts.file.url
        lines = codecs.open(fn, 'rb', 'utf8').readlines()
        querysetlist=[]
        for line in lines:
            querysetlist.append(Cdkeys_Table(gifts=gifts, cdkey=line.rstrip('\r\n')))
        Cdkeys_Table.objects.bulk_create(querysetlist)
import_cdkeys.short_description = u'导入兑换码'

class GiftsAdmin(admin.ModelAdmin):
    actions = [import_cdkeys, ]
    list_display = ['subject', 'times', 'rate']
    search_fields = ['subject', ]
    list_filter = ['post']

class CdkeysTableAdmin(admin.ModelAdmin):
    list_display = ['gifts', 'cdkey']
    list_filter = ['gifts']
    search_fields = ['gifts', ]

class CdkeysRecordAdmin(admin.ModelAdmin):
    list_display = ['gifts', 'user', 'cdkey']
    list_filter = ['gifts']
    search_fields = ['gifts', ]
    raw_id_fields = ('user', 'gifts')

admin.site.register(Gifts,GiftsAdmin)
admin.site.register(Cdkeys_Table,CdkeysTableAdmin)
admin.site.register(Cdkeys_Record,CdkeysRecordAdmin)
