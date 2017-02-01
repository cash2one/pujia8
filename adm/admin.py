from models import Adm, Material, Game_ads
from django.contrib import admin

class MaterialInline(admin.TabularInline):
    model = Material
    extra = 1

class AdmAdmin(admin.ModelAdmin):
    model = Adm
    inlines = [MaterialInline]

def fix_timespan_0(modeladmin, request, queryset):
    for game_ads in queryset:
        game_ads.timespan = 0
        game_ads.save(update_fields = ['timespan'])
fix_timespan_0.short_description = u'时间间隔：关闭'

def fix_timespan_2(modeladmin, request, queryset):
    for game_ads in queryset:
        game_ads.timespan = 2
        game_ads.save(update_fields = ['timespan'])
fix_timespan_2.short_description = u'时间间隔：2分钟'

def fix_timespan_5(modeladmin, request, queryset):
    for game_ads in queryset:
        game_ads.timespan = 5
        game_ads.save(update_fields = ['timespan'])
fix_timespan_5.short_description = u'时间间隔：5分钟'

def fix_ad(modeladmin, request, queryset):
    for game_ads in queryset:
        # if game_ads.channel not in [u'xm', u'az', u'hack', u'zy']:
        #     game_ads.banner = 4
        #     game_ads.inst = 4
        #     game_ads.splash = 2
        # if game_ads.channel == 'zy':
        game_ads.banner = 4
        game_ads.inst = 4
        game_ads.splash = 2
        game_ads.VersionCode = 21
        game_ads.patch_url = ''
        game_ads.adview_key = 'SDK20161824060635gsp6rhquo26wl5a'
        game_ads.save()
fix_ad.short_description = u'修正广告位'

class Game_adsAdmin(admin.ModelAdmin):
    model = Game_ads
    actions = [fix_timespan_0, fix_timespan_2, fix_timespan_5, fix_ad]
    list_display = ['package', 'channel', 'banner', 'inst', 'splash', 'timespan', 'sms']
    list_filter = ['channel', 'sms']
    search_fields = ['package', ]

admin.site.register(Adm, AdmAdmin)
admin.site.register(Game_ads, Game_adsAdmin)
