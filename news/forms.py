# -*- coding: utf-8 -*-
from django import forms
from django.forms import widgets
from django.forms import ModelForm
from models import News, Category, Comments

from django.contrib.auth.models import User
import datetime


class NewsForm(forms.ModelForm):
    title = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'size': '100'}))
    text = forms.CharField(label='NEWS', widget=forms.Textarea(), required=True)
#    date = forms.DateTimeField(initial = datetime.date.today, label='Дата', input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'))
    link = forms.URLField(widget = widgets.URLInput())
    author = forms.CharField(label='Автор', max_length=50)
    category = forms.ModelChoiceField(queryset = Category.objects.all(), required=False) 
    comments = forms.ModelChoiceField(queryset = Comments.objects.all(), required=False)

    class Meta:
        model = News
        fields = '__all__'
        exclude = ['user', 'date']