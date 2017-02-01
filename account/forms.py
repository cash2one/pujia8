# -*- coding:utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from django.contrib import auth


class RegisterForm(forms.Form):
    username = forms.CharField(label=u"帐号", max_length=10, widget=forms.TextInput(attrs={'size': 20, }))
    password = forms.CharField(label=u"密码", max_length=30, widget=forms.PasswordInput(attrs={'size': 20, }))
    password2 = forms.CharField(label=u"确认密码", max_length=30, widget=forms.PasswordInput(attrs={'size': 20, }))
    email = forms.EmailField(label=u"邮箱", max_length=30, widget=forms.TextInput(attrs={'size': 30, }))
    avatar = forms.ImageField(label=u'头像（如不方便上传可忽视）', required=False)

    def clean_username(self):
        """验证重复昵称"""
        username2 = self.cleaned_data["username"]
        if ' ' in username2 or '　' in username2:
            raise forms.ValidationError(u"昵称里面不可包含空格")
        users = User.objects.filter(username__iexact=username2)
        if not users:
            return username2
        raise forms.ValidationError(u"该昵称已经被使用")

    def clean_email(self):
        """验证重复email"""
        emails = User.objects.filter(email__iexact=self.cleaned_data["email"])
        if not emails:
            return self.cleaned_data["email"]
        raise forms.ValidationError(u"该邮箱已经被使用")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(u"密码不一致")
        return password2


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label=u"原密码", max_length=30, widget=forms.PasswordInput(attrs={'size': 20, }))
    new_password = forms.CharField(label=u"新密码", max_length=30, widget=forms.PasswordInput(attrs={'size': 20, }))
    conf_password = forms.CharField(label=u"确认新密码", max_length=30, widget=forms.PasswordInput(attrs={'size': 20, }))


class LoginForm(forms.Form):
    username = forms.CharField(label=u"帐号", max_length=30, widget=forms.TextInput(attrs={'size': 20, }))
    password = forms.CharField(label=u"密码", max_length=30, widget=forms.PasswordInput(attrs={'size': 20, }))

    def clean_username(self):
        global username
        username = self.cleaned_data["username"]
        users = User.objects.filter(username__iexact=username)
        if not users:
            raise forms.ValidationError(u"查无此账号")
        return username

    def clean_password(self):
        password = self.cleaned_data["password"]
        user = auth.authenticate(username=username, password=password)
        if user is None or not user.is_active:
            raise forms.ValidationError(u"密码和账号不匹配")
        return password

