from models import Tail
from django.contrib import admin

class TailAdmin(admin.ModelAdmin):
    raw_id_fields = ('user', 'tar_user')
    list_display = ['content', 'user']
    search_fields = ['user__username', 'content']

admin.site.register(Tail,TailAdmin)
