from django.forms import ModelForm
from django import forms

from www.models import *

class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = (['title', 'status', 'show_gallery', 'html_message'])
        labels = {
            'title': 'Titol de la pàgina',
            'status': 'Estat',
            'show_gallery': 'Mostra galeria de fotos',
            'html_message': 'Contingut',
        }

class AreYouSureForm(forms.Form):
    pass