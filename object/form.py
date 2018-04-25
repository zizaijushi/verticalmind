from django import forms
from .models import UserObject,Report

class UserObjectForm(forms.ModelForm):
    class Meta:
        model = UserObject
        fields = ('OBJECT',)

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('TITLE','BODY')