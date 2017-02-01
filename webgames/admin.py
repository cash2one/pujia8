from models import Puji, Pay_PP
from django.contrib import admin

class PujiAdmin(admin.ModelAdmin):
    raw_id_fields = ('user', )
    list_display = ['add_time', 'user', 'serverid']
    search_fields = ['user__username', ]

class PayPPAdmin(admin.ModelAdmin):
    raw_id_fields = ('user', )
    list_display = ['user', 'value', 'serverid']
    search_fields = ['user__username', ]

admin.site.register(Puji,PujiAdmin)
admin.site.register(Pay_PP,PayPPAdmin)
