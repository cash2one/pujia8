from models import PujiaComment, CommentPositive
from django.contrib import admin

def del_spam(modeladmin, request, queryset):
    for c in queryset:
        if len(c.content) < 10:
            c.delete()
del_spam.short_description = u'删除灌水'

def update_hot(modeladmin, request, queryset):
    for c in queryset:
        c.hot = True
        c.positive = 5
        c.save(update_fields = ['hot', 'positive'])

        u = c.name.get_profile()
        u.pp += 20
        u.super_comment += 1
        u.save(update_fields = ['pp', 'super_comment'])
update_hot.short_description = u'设为热门'

class PujiaCommentAdmin(admin.ModelAdmin):
    actions = [del_spam, update_hot]
    list_display = ['content', 'hot', 'Target', 'name']
    search_fields = ['content', 'target']
    raw_id_fields = ('name', )
    list_filter = ['hot']

    def Target(self, obj):
        return '<a target="_blank" href="%s">%s</a>'%(obj.target, obj.target)
    Target.allow_tags = True
    Target.short_description = u'对象'

class CommentPositiveAdmin(admin.ModelAdmin):
    list_display = ['user', 'comment']
    raw_id_fields = ('user', 'comment')

admin.site.register(PujiaComment, PujiaCommentAdmin)
admin.site.register(CommentPositive, CommentPositiveAdmin)
