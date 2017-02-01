# -*- coding:utf-8 -*-

from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from api.views import get_user_info, games2json, flows2json, topics2json, users2json
try:
    from django.contrib.auth import get_user_model
except ImportError: # Django < 1.5
    from django.contrib.auth.models import User
else:
    User = get_user_model()

from games.models import Games
from flow.models import Flow
from forum.models import Topic
from tokenapi.tokens import token_generator
from tokenapi.http import JsonResponse, JsonError, JsonResponseForbidden, JsonResponseUnauthorized
from base64 import b64decode
import json

# Creates a token if the correct username and password is given
# token/new.json
# Required: username&password
# Returns: success&token&user
@csrf_exempt
def token_new(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = authenticate(username=username, password=password)

            if user:
                TOKEN_CHECK_ACTIVE_USER = getattr(settings, "TOKEN_CHECK_ACTIVE_USER", False)

                if TOKEN_CHECK_ACTIVE_USER and not user.is_active:
                    return JsonResponseForbidden("User account is disabled.")

                data = {
                    'token': token_generator.make_token(user),
                    'user': user.pk,
                    'msg': u'登录成功',
                    'user_info': get_user_info(user)['user_info'],
                    'notification_num': user.get_profile().notification,
                    'all_user': {}
                }
                app_sync = user.get_profile().app_sync
                if app_sync:
                    app_sync = json.loads(b64decode(app_sync))
                    if 'game_col' in app_sync:
                        games = Games.objects.select_related().filter(id__in = app_sync['game_col']).order_by('-add_time')
                        app_sync['game_col'] = games2json(games)
                    if 'toutiao_col' in app_sync:
                        flows = Flow.objects.select_related().filter(id__in = app_sync['toutiao_col']).order_by('-add_time')
                        app_sync['toutiao_col'] = flows2json(flows)
                    if 'bbs_col' in app_sync:
                        topics = Topic.objects.select_related().filter(id__in = app_sync['bbs_col']).order_by('-created_on')
                        app_sync['bbs_col'] = topics2json(topics)
                    if 'toutiao_usersub' in app_sync:
                        users = User.objects.select_related().filter(id__in = app_sync['toutiao_usersub'])
                        app_sync['toutiao_usersub'] = users2json(users)
                    data['all_user'] = app_sync

                return JsonResponse(data)
            else:
                return JsonResponseUnauthorized("账号密码不一致，请重试。")
        else:
            return JsonError("请填写账号以及密码。")
    else:
        return JsonError("Must access via a POST request.")

# Checks if a given token and user pair is valid
# token/:token/:user.json
# Required: user
# Returns: success
def token(request, token, user):
    try:
        user = User.objects.get(pk=user)
    except User.DoesNotExist:
        return JsonError("User does not exist.")

    TOKEN_CHECK_ACTIVE_USER = getattr(settings, "TOKEN_CHECK_ACTIVE_USER", False)

    if TOKEN_CHECK_ACTIVE_USER and not user.is_active:
        return JsonError("User account is disabled.")

    if token_generator.check_token(user, token):
        return JsonResponse({})
    else:
        return JsonError("Token did not match user.")

