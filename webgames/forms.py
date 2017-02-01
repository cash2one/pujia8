# -*- coding:utf-8 -*-

from django import forms

SERVER_CHOICES = (
        ('0', '————————'),
        ('1', '一区：狩猎之森'),
        ('2', '二区：巨铁山脉'),
        ('3', '三区：密语森林'),
        )

class ServerForm(forms.Form):
    serverid = forms.ChoiceField(label='服务区', choices=SERVER_CHOICES,
        widget=forms.Select(attrs={'style':'font-size: 12px; width: 180px; height: 26px'}), required=False)
