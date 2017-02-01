# -*- coding:utf-8 -*-

from django import forms
from models import Gallery

GALLERY_ORDER_BY_CHOICES = (
        ('-add_time', '添加日期'),
        ('-count', '喜欢数'),
        )

class GalleryOrderByForm(forms.Form):
    gallery_order_by = forms.ChoiceField(label='排序', choices=GALLERY_ORDER_BY_CHOICES,
        widget=forms.Select(attrs={'style':'font-size: 12px; width: 90px; height: 26px'}), required=False)
