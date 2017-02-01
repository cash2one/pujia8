from models import *
from django.contrib import admin
from django import forms
from django.core.urlresolvers import reverse

from views import make_tag
import time

class ChannelAdmin(admin.ModelAdmin):
    model = Channel

class ColumnAdmin(admin.ModelAdmin):
    model = Column

class FlowForm(forms.ModelForm):
    head_img = forms.ChoiceField(label='头图', choices=[], required=False)
    def __init__(self, *args, **kwargs):
        super(FlowForm, self).__init__(*args, **kwargs)
        try:
            pics_list = re.findall('/static/[a-zA-z0-9/\.]+[jpg|JPG|jpeg|JPEG|png|PNG]', kwargs['instance'].content)
            if kwargs['instance'].head_img:
                pics_list.append(kwargs['instance'].head_img)
            self.fields["head_img"].choices = [(p, p) for p in pics_list]
        except:
            pass
    class Meta:
        model = Flow
        exclude = ('comment', 'count')

def sticky(modeladmin, request, queryset):
    for flow in queryset:
        try:
            flow.sticky = not flow.sticky
            flow.save()
        except:
            pass
sticky.short_description = u'置顶/取消置顶'

def fix_hot(modeladmin, request, queryset):
    for flow in queryset:
        try:
            flow.hot = not flow.hot
            flow.save()
        except:
            pass
fix_hot.short_description = u'热门/取消热门'

def fix_post(modeladmin, request, queryset):
    for flow in queryset:
        try:
            flow.post = not flow.post
            flow.save()
        except:
            pass
fix_post.short_description = u'发布/取消发布'

def fix_bili(modeladmin, request, queryset):
    for flow in queryset:
        if u'bilibili.com' in flow.url:
            video_info = Video_info.objects.select_related().filter(flow_id=flow.id)
            if not video_info.exists():
                bilibili = BiliBili(flow.url)
                name = 'cover/' + os.path.basename(bilibili['cover_pic'])
                pic_dat = urllib2.urlopen(bilibili['cover_pic']).read()
                fn = os.path.dirname(__file__)[:-4] + 'static/' + name
                dst = open(fn, 'wb')
                dst.write(pic_dat)
                dst.close()
                u = Video_info(flow=flow, cid=bilibili['cid'], cover=name, duration=bilibili['duration'])
                u.save()
fix_bili.short_description = u'更新B站视频信息'

class FlowAdmin(admin.ModelAdmin):
    form = FlowForm
    actions = [sticky, fix_bili, fix_hot, fix_post]
    list_display = ['title', 'hot', 'post', 'user', 'count', 'comment', 'show_ui']
    raw_id_fields = ('user',)
    list_filter = ['channel', 'column', 'verify', 'post', 'sticky', 'hot', 'add_time']
    filter_horizontal = ('column', 'channel')
    search_fields = ['title', 'user__username']

    def show_ui(self, obj):
        return '<a target="_blank" href="%s">查看</a>'%reverse("news_info", args=[obj.pk])
    show_ui.allow_tags = True
    show_ui.short_description = u'在前台查看'

class VideoinfoAdmin(admin.ModelAdmin):
    model = Video_info
    search_fields = ['flow__title']
    raw_id_fields = ('flow',)

class SubscriptionAdmin(admin.ModelAdmin):
    model = Subscription
    search_fields = ['src_user__username']
    raw_id_fields = ('src_user', 'desc_user')

class CollectionnAdmin(admin.ModelAdmin):
    model = Collection
    search_fields = ['user__username']
    raw_id_fields = ('user', 'flow')

class Hot_tagAdmin(admin.ModelAdmin):
    model = Hot_tag
    list_display = ['src', 'tag']
    search_fields = ['tag', 'tag']

class Subscription_TagAdmin(admin.ModelAdmin):
    model = Subscription_Tag
    search_fields = ['user__username']
    raw_id_fields = ('user', 'tag')

admin.site.register(Channel, ChannelAdmin)
admin.site.register(Column, ColumnAdmin)
admin.site.register(Flow, FlowAdmin)
admin.site.register(Video_info, VideoinfoAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Collection, CollectionnAdmin)
admin.site.register(Hot_tag, Hot_tagAdmin)
admin.site.register(Subscription_Tag, Subscription_TagAdmin)
