from models import Gallery
from django.contrib import admin

class GalleryAdmin(admin.ModelAdmin):
    raw_id_fields = ('user', )
    list_display = ['imagefile', 'user']
    search_fields = ['user__username', 'imagefile']

admin.site.register(Gallery,GalleryAdmin)
