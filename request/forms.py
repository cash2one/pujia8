# -*- coding:utf-8 -*-
from django import forms

class GameRequestForm(forms.Form):
    CATEGORY_CHOICES = (
        (u'0', u'NDS'),
        (u'1', u'PSP'),
        (u'2', u'WII'),
        (u'3', u'PS2'),
        (u'4', u'GBA'),
        (u'5', u'IPHONE'),
        (u'8', u'ANDROID'),
        (u'6', u'PC'),
        (u'7', u'ETC'),
    )
    title = forms.CharField(label='游戏名称',max_length=100)
    category = forms.ChoiceField(label='游戏平台',choices=CATEGORY_CHOICES)
    gamepack = forms.ImageField(label='游戏封面')
    publish_time = forms.DateField(label='发售日期')
    game_type = forms.CharField(required=False,label='游戏类型',max_length=30)
    download_link = forms.CharField(label='下载地址',max_length=300)
    introduce = forms.CharField(widget=forms.Textarea(),label='游戏介绍',max_length=5000)
    caption = forms.CharField(widget=forms.Textarea(),label='请愿说明',max_length=5000)
