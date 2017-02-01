from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('pujiahh.webgames.views',
    (r'^xsqst/$', xsqst),
    (r'^xsqst/exchange/gold/$', exchange_gold),
    (r'^xsqst/exchange/puji/$', exchange_puji),
    (r'^xsqst/exchange/pp/$', get_pay_pp),
    (r'^yxhg/$', yxhg),
    (r'^yxhg/play/$', yxhg_play),
    (r'^jjdjl/$', jjdjl),
    (r'^jjdjl/play/$', jjdjl_play),
    (r'^czdtx/$', czdtx),
    (r'^sdgundam/$', sdgundam),
    (r'^bspt/$', bspt),
)
