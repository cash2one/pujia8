# -*- coding:utf-8 -*-
from django import forms
from models import PujiaComment

class EditCommentForm(forms.ModelForm):
    class Meta:
        model = PujiaComment
        fields = ('content',)

COMMENTS_ORDER_BY_CHOICES = (
    ('-date', '正序'),
    ('date', '倒序'),
)

class CommentsOrderForm(forms.Form):
    comments_order_by = forms.ChoiceField(label='排序', choices=COMMENTS_ORDER_BY_CHOICES,
    widget=forms.Select(attrs={'style':'font-size: 12px; width: 60px; height: 26px'}), required=False)

