from models import GameRequest
from django.contrib import admin

class GameRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'up', 'down', 'ip']
    search_fields = ['title',]
    list_filter = ['category',]
    raw_id_fields = ('name', )

admin.site.register(GameRequest,GameRequestAdmin)
