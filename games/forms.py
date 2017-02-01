# -*- coding:utf-8 -*-

from django import forms
from models import Games

GAMES_STATE_CHOICES = (
        ('1','已发布'),
        ('2','汉化中'),
        )

class GameForm(forms.ModelForm):
    state = forms.ChoiceField(label='汉化状态', choices=GAMES_STATE_CHOICES, required=False)
    class Meta:
        model = Games
        fields = ['title_cn', 'title_src', 'platform', 'language', 'imagefile', \
                  'team', 'level', 'publish_time', 'game_size', \
                  'publish_url', 'tags', 'download_link','content', 'state', 'review_id', 'gospel_id']
        widgets = {
            'publish_time': forms.DateInput(attrs={'placeholder': '填写格式：2014-01-01'}),
            'publish_url': forms.TextInput(attrs={'placeholder': '请填原发布帖网址，原创可留空'}),
            'tags': forms.TextInput(attrs={'placeholder': '可填多个标签，用空格或逗号隔开'}),
            'review_id': forms.TextInput(attrs={'placeholder': '如帖子/topic/9521/，ID为9521'}),
            'gospel_id': forms.TextInput(attrs={'placeholder': '如上，可留空'}),
        }

GAMES_ORDER_BY_CHOICES = (
        ('-publish_time', '发布日期'),
        ('-add_time', '添加日期'),
        ('-count', '人气最高'),
        ('-comments_count', '评论最多'),
        )

class GameOrderForm(forms.Form):
    games_order_by = forms.ChoiceField(label='排序', choices=GAMES_ORDER_BY_CHOICES,
        widget=forms.Select(attrs={'style':'font-size: 12px; width: 90px; height: 26px'}), required=False)

class GameStateForm(forms.Form):
    games_state = forms.ChoiceField(label='状态', choices=GAMES_STATE_CHOICES,
        widget=forms.Select(attrs={'style':'font-size: 12px; width: 90px; height: 26px'}), required=False)

LANGUAGE_CHOICES = (
        ('all', '全部'),
        ('cn', '中文汉化'),
        ('en', '英文'),
        ('jp', '日文'),
        )

class GameLanguageForm(forms.Form):
    game_language = forms.ChoiceField(label='语言', choices=LANGUAGE_CHOICES,
        widget=forms.Select(attrs={'style':'font-size: 12px; width: 90px; height: 26px'}), required=False)
