from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt

from functools import wraps

def token_required(view_func):
    """Decorator which ensures the user has provided a correct user and token pair."""

    @csrf_exempt
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = None
        token = None

        if not (user and token):
            user = request.POST['user']
            token = request.POST['token']

            if not user or not token:
                return HttpResponseForbidden("Must include 'user' and 'token' parameters with request.")

        if user and token:
            user = authenticate(pk=user, token=token)
            if user:
                login(request, user)
                return view_func(request, *args, **kwargs)

        return HttpResponseForbidden('{"state": 2}')
    return _wrapped_view
