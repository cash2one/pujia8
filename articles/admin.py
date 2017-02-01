from models import Articles
from django.contrib import admin
from sgmllib import SGMLParser
from forum.models import Topic, Post

tt = {
    u'0': 6,
    u'1': 7,
    u'2': 8,
    u'3': 9,
    u'4': 10,
    u'5': 11,
    u'6': 12,
    u'7': 16,
    u'99': 15,
    }

class html2txt(SGMLParser):
    txt = ''
    def reset(self):
        self.text = ''
        SGMLParser.reset(self)

    def start_img(self, attrs):
        self.is_img=1
        src = [v for k, v in attrs if k=='src']
        if src:
            self.txt += '\r\n'.join(src)+'\r\n'

    def handle_data(self,text):
        self.txt += text+'\r\n'

def c2f(modeladmin, request, queryset):
    tid = 300
    pid = 1200
    for a in queryset:
        if a.subject == u'1':
            parser = html2txt()
            parser.feed(a.content)
            parser.close()
            message = parser.txt
            forum_id = 8
            subject = '%s'%(a.title)
            last_reply_on = a.time
            posted_by_id = a.name.id
            poster_ip = '1.1.1.1'
            created_on = a.time

            t = Topic(id = tid, forum_id = forum_id, posted_by_id = posted_by_id,\
                subject = subject, post_id = pid, created_on = created_on, last_reply_on = last_reply_on)
            t.save()

            p = Post(id = pid, topic_id = tid, posted_by_id = posted_by_id, poster_ip = poster_ip, topic_post = True, message = message, created_on = created_on)
            p.save()

            tid += 1
            pid += 1
c2f.short_description = u'复制至社区'

class ArticlesAdmin(admin.ModelAdmin):
    actions = [c2f]
    list_display = ['title', 'count', 'id', 'category']
    search_fields = ['title']
    raw_id_fields = ('name',)
    list_filter = ['category']
    radio_fields = {'post': admin.HORIZONTAL,'hot': admin.HORIZONTAL,\
                    'html': admin.HORIZONTAL,'source': admin.HORIZONTAL}
    fieldsets = (
        (u'基本信息', {
            'fields': ('title', 'subject', 'name', 'category', 'category2', \
                       'source', 'sourceurl', 'team', 'label', 'content', 'count')
        }),
        (u'高级设置', {
            'classes': ('collapse',),
            'fields': ('post', 'hot', 'html')
        }),
    )

admin.site.register(Articles,ArticlesAdmin)
