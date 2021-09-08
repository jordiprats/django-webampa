from django.forms import ModelForm
from django import forms

from www.models import *

class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = (['title', 'status', 'show_blog', 'show_gallery', 'html_message'])
        labels = {
            'title': 'Titol de la pàgina',
            'status': 'Estat',
            'show_blog': 'Habilita blog',
            'show_gallery': 'Mostra galeria de fotos',
            'html_message': 'Contingut',
        }

class BlogForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = (['title', 'status', 'post_date', 'show_gallery', 'html_message'])
        widgets = {
            'post_date': forms.DateInput(format=('%Y-%m-%d'), attrs={"type": 'date'}),
        }
        labels = {
            'title': 'Titol de la pàgina',
            'status': 'Estat',
            'post_date': 'Data del post',
            'show_gallery': 'Mostra galeria de fotos',
            'html_message': 'Contingut',
        }

class AreYouSureForm(forms.Form):
    pass