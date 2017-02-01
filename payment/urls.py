from django.conf.urls.defaults import *
from django.views.generic import TemplateView
from views import *

urlpatterns = patterns('',
	url(r'^$', TemplateView.as_view(template_name="payment/index.html"), name="payment_index"),
    url(r'^(?P<value>\d+)/$', payment, name="payment_upgrade_plans"),
    url(r'^success/$', TemplateView.as_view(template_name="payment/success.html"), name="payment_success"),
    url(r'^error/$', TemplateView.as_view(template_name="payment/error.html"), name="payment_error"),
    url(r'^return_url$', return_url_handler, name="payment_return_url"),
    url(r'^notify_url$', notify_url_handler, name="payment_notify_url"),
)
