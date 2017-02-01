from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from models import Articles
from forms import NewForm, TopicForm
from django.views.generic import TemplateView, CreateView
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from account.models import Profile
from games.models import Games
from django.core.cache import cache
from django.db.models import Q


def news(request):
    news = Articles.objects.select_related().filter(Q(post='1'),Q(subject__in=['0','2']) | Q(subject='1', html='0')).order_by('-time')
    return render_to_response('news.html',{'news': news},
                              context_instance=RequestContext(request))

def topics(request):
    teachings = Articles.objects.select_related().filter(subject='1',post='1').order_by('-time')
    return render_to_response('topics.html',{'teachings': teachings},
                              context_instance=RequestContext(request))

def article_detail(request, aid):
    article = Articles.objects.select_related().get(pk=aid)
    article.count+=1
    article.save()
    article_user = User.objects.select_related().get(id=article.name_id)
    try:
        user_profile = article_user.get_profile()
    except :
        import time
        today = time.strftime("%Y-%m-%d", time.localtime())
        profile = Profile(user=article_user, count=0, today=today, todaycount=0)
        profile.save()
        user_profile = article_user.get_profile()

    perm_edit_article = False
    if request.user == article.name:
        perm_edit_article = True
    if article.subject == '0':
        subject = 'new'
    else:
        subject = 'topic'
    article_label_list = Articles.objects.select_related().filter(label=article.label,post='1').order_by('-time')
    if len(article_label_list)<2:
        article_label_list=None
    if article.label==None or article.label=='':
        article_label_list=None

    article_hot_list = cache.get('article_hot_list')
    if not article_hot_list:
        article_hot_list = Articles.objects.select_related().filter(hot='1',post='1').order_by('-time')[:10]
        cache.set('article_hot_list', article_hot_list, 900)
    game_hot_list = cache.get('game_hot_list')
    if not game_hot_list:
        game_hot_list = Games.objects.select_related().filter(post='1').order_by('-count')[:10]
        cache.set('game_hot_list', game_hot_list, 900)
    return render_to_response('article_detail.html', {'article': article, 'subject':subject,\
                                                'article_label_list':article_label_list, 'game_hot_list': game_hot_list, \
                                                'article_hot_list':article_hot_list,\
                                                'perm_edit_article': perm_edit_article,\
                                                'user_profile': user_profile},
                              context_instance=RequestContext(request))

class SubmitNew(CreateView):
    model = Articles
    form_class = NewForm
    template_name = "submit_articles.html"
    success_view_name = "news"

    def get_form_kwargs(self):
        kwargs = super(SubmitNew, self).get_form_kwargs()
        kwargs['instance'] = Articles()
        if self.request.user.is_authenticated():
            kwargs['instance'].subject = '0'
            kwargs['instance'].name = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super(SubmitNew, self).form_valid(form)
        return response

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        else:
            return reverse(self.success_view_name)

class SubmitTopic(CreateView):
    model = Articles
    form_class = TopicForm
    template_name = "submit_articles.html"
    success_view_name = "topics"

    def get_form_kwargs(self):
        kwargs = super(SubmitTopic, self).get_form_kwargs()
        kwargs['instance'] = Articles()
        if self.request.user.is_authenticated():
            kwargs['instance'].subject = '1'
            kwargs['instance'].name = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super(SubmitTopic, self).form_valid(form)
        return response

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        else:
            return reverse(self.success_view_name)

def article_edit(request, subject, aid):
    article = Articles.objects.select_related().get(pk=aid)

    perm_edit_article = False
    if request.user == article.name:
        perm_edit_article = True

    if subject == 'new':
        form = NewForm(instance = article)
    elif subject == 'topic':
        form = TopicForm(instance = article)

    if request.method == 'POST':
        article.title = request.POST['title']
        article.category = request.POST['category']
        article.label = request.POST['label']
        article.content = request.POST['content']
        if subject == 'new':
            article.source = request.POST['source']
            article.sourceurl = request.POST['sourceurl']
            article.team = request.POST['team']
        elif subject == 'topic':
            article.category2 = request.POST['category2']
        article.save()
        return HttpResponseRedirect('/articles/%s/'%aid)
    return render_to_response("article_edit.html",{'form': form, 'perm_edit_article': perm_edit_article},\
                        context_instance=RequestContext(request))
