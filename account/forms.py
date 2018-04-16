from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label='密码',widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='重复密码',widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username','email')

    def clean_password_confirm(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password_confirm']:
            raise forms.ValidationError("两次输入密码不匹配！请重新输密码！")
        return cd['password_confirm']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('phone','birth','weixin','company','title')