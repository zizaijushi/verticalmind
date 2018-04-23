from django import forms
from .models import Dailyreplay

class Dailyreplayfrom(forms.ModelForm):
    class Meta:
        model = Dailyreplay
        fields = ('NAME',)
