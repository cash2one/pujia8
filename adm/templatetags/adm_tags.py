#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from django import template
from adm.models import Adm, Material
import random

register = template.Library()

@register.simple_tag
def show_ad(slug):
    ads = Material.objects.select_related().filter(adm__slug = slug, post = True)
    ads_full = []
    for ad in ads:
        ads_full.extend([ad for i in range(ad.weight)])
    if ads_full:
	    ad = random.choice(ads_full)
	    return '''<a target="_blank" title="%s" href="%s?utm_source=%s&utm_medium=adm&utm_campaign=%s"><img src="%s" alt="%s"></a>'''%(ad.title, ad.link, slug, ad.title, ad.imagefile.url, ad.title)
    else:
        return ''