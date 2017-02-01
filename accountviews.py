from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from pujia_comments.models import PujiaComment

def profile(request, user_id=None, template_name="lbforum/account/profile.html"):
    view_user = request.user
    if user_id:
        view_user = get_object_or_404(User, pk = user_id)
    view_only = view_user != request.user
    hot_comments = PujiaComment.objects.select_related().filter(name = view_user, hot = True).order_by('-date')
    ext_ctx = {'view_user':view_user, 'view_only':view_only, 'hot_comments':hot_comments}
    return render(request, template_name, ext_ctx)

