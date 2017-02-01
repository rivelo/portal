# -*- coding: utf-8 -*-
from django import forms
from django.forms import widgets
from django.forms import ModelForm
from models import Events, RegEvent, BikeType, EventType

from django.contrib.auth.models import User
import datetime


class EventsForm(forms.ModelForm):
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'size': '100'}))
    text = forms.CharField(label='Положення/реклама', widget=forms.Textarea(attrs={'class':'editable'}), required=True)
    type = forms.ModelMultipleChoiceField(queryset = EventType.objects.all(), label='Категорії') 
    url = forms.URLField(widget = widgets.URLInput(attrs={'size': '80'}), required=False, label='Інтернет сторінка')
    reg_url = forms.CharField(max_length=255, required=False, label='Посилання на реєстрацію')
#    reg_status = forms.BooleanField(label='Відкрита реєстрація')
    gps_track = forms.CharField(max_length=255, required=False, label='Посилання на GPS трек')
    photo = forms.ImageField(required=False, label='Фото афіши')
    icon = forms.ImageField(required=False, label='Логотип')
    forum_url = forms.URLField(widget = widgets.URLInput(attrs={'size': '80'}), required=False, label='Посилання на форум')
    city = forms.CharField(max_length=100, required=False, label='Місто')
    lat = forms.DecimalField(max_digits=9, decimal_places=6, required=False, label='Широта')
    lng = forms.DecimalField(max_digits=9, decimal_places=6, required=False, label='Довгота')
    description = forms.CharField(widget=forms.Textarea(), required=False, label='Опис')
    date = forms.SplitDateTimeField(label='Дата', input_date_formats=["%d.%m.%Y"], input_time_formats=["%H:%M"])
                                    #input_formats=['%d.%m.%Y', '%d/%m/%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y'))
#    initial = datetime.datetime.today,
#    user = forms.ModelChoiceField(queryset = User.objects.all(), required=True, label='Користувач')

#    type = models.ManyToManyField(Type, blank=True) # ForeignKey(Type, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        model = Events
        fields = '__all__'
        exclude = ['user', 'pub_date', 'date', 'rules']