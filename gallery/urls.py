from django.conf.urls.defaults import *
from views import *
from models import Gallery

urlpatterns = patterns('pujiahh.gallery.views',
    (r'^$', index),
)
