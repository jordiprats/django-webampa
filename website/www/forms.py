from django.forms import ModelForm
from django import forms

from www.models import *

class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = (['title', 'status', 'html_message'])
        labels = {
            'title': 'Titol de la pàgina',
            'status': 'Estat',
            'html_message': 'Contingut',
        }
