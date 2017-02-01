from models import *
from django.contrib import admin

class Emoji_img_Inline(admin.TabularInline):
    model = Emoji_img
    extra = 1

class EmojiAdmin(admin.ModelAdmin):
    model = Emoji
    inlines = [Emoji_img_Inline]

admin.site.register(Emoji, EmojiAdmin)
