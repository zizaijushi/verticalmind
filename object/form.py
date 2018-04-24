from django import forms
from .models import UserObject

class UserObjectForm(forms.ModelForm):
    class Meta:
        model = UserObject
        fields = ('OBJECT',)