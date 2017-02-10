# -*- coding: utf-8 -*-
from django import forms
from django.forms import widgets
from django.forms.extras.widgets import SelectDateWidget
from django.forms import ModelForm
from models import Events, RegEvent, BikeType, EventType

from django.contrib.auth.models import User
import datetime


class EventsForm(forms.ModelForm):
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'size': '60'}))
    text = forms.CharField(label='Положення/реклама', widget=forms.Textarea(attrs={'class':'editable'}), required=True)
    type = forms.ModelMultipleChoiceField(queryset = EventType.objects.all(), label='Категорії') 
    url = forms.URLField(widget = widgets.URLInput(), required=False, label='Інтернет сторінка')
    reg_url = forms.CharField(max_length=255, required=False, label='Посилання на реєстрацію')
#    reg_status = forms.BooleanField(label='Відкрита реєстрація')    
    gps_track = forms.CharField(max_length=255, required=False, label='Посилання на GPS трек', widget=forms.TextInput(attrs={'size': '70'}))
    photo = forms.ImageField(required=False, label='Фото афіши')
    icon = forms.ImageField(required=False, label='Логотип')
    forum_url = forms.URLField(widget = widgets.URLInput(), required=False, label='Посилання на форум')
    city = forms.CharField(max_length=100, required=False, label='Місто')
    lat = forms.DecimalField(max_digits=9, decimal_places=6, required=False, label='Широта')
    lng = forms.DecimalField(max_digits=9, decimal_places=6, required=False, label='Довгота')
#    date = forms.SplitDateTimeField(label='Дата', input_date_formats=["%d.%m.%Y"], input_time_formats=["%H:%M"])
    date = forms.DateTimeField(initial = datetime.datetime.today, input_formats=['%d.%m.%Y'], widget=forms.DateTimeInput(format='%d.%m.%Y', attrs={'id':"event_datepicker"}), required=False)
    time = forms.TimeField(initial = "12:00", input_formats=['%H:%M'], required=False)
    description = forms.CharField(widget=forms.Textarea(), required=False, label='Опис')
    
    class Meta:
        model = Events
        fields = '__all__'
        exclude = ['user', 'pub_date', 'rules']
        
cur_year = datetime.datetime.today()
x = range(cur_year.year-70, cur_year.year)
YEAR_CHOICES = tuple(x)
MONTH_CHOISES = {1:("Січень"), 2:("Лютий"), 3:("Березень"), 4:("Квітень"), 5:("Травень"), 6:("Червень"), 7:("Липень"), 8:("Серпень"), 9:("Вересень"), 10:("Жовтень"), 11:("Листопад"), 12:("Грудень")}
SEX_CHOICES = ((1, 'Чоловіча'), (0, 'Жіноча'))
        
class RegEventsForm(forms.ModelForm):
    event = forms.ModelChoiceField(queryset = Events.objects.all(), label='Захід') 
    fname = forms.CharField(label='Імя', max_length=100, widget=forms.TextInput(attrs={'size': '50'}), error_messages={'required': 'Заповніть поле Імя. Це є обовязкове поле.'})
    lname = forms.CharField(label='Прізвище', widget=forms.TextInput(attrs={'size': '50'}), required=True, error_messages={'required': 'Заповніть поле Прізвище. Це є обовязкове поле.'})
    sex = forms.ChoiceField(label='Стать', choices=SEX_CHOICES)
    email = forms.EmailField(help_text='Введіть адресу на яку буде відправлено підтвердження', error_messages={'required': 'Це є обовязкове поле.'})
    phone = forms.CharField(max_length=13, label='Телефон', help_text='Телефон у міжародному форматі. Приклад: +380XX1234567', error_messages={'required': 'Це є обовязкове поле.'})
    country = forms.CharField(max_length=100, required=False, label='Країна')
    city = forms.CharField(max_length=100, required=False, label='Місто')
    club = forms.CharField(max_length=255, required=False, label='Команда')
    bike_type = forms.ModelChoiceField(label='Тип велосипеду', queryset = BikeType.objects.all()) 
    birthday = forms.DateField( widget=SelectDateWidget(years=YEAR_CHOICES, months=MONTH_CHOISES), label='Дата народження',) #input_formats=['%d.%m.%Y'],
    description = forms.CharField(widget=forms.Textarea(attrs={'cols': 93, 'rows': 8}), required=False, label='Примітки')

    class Meta:
        model = RegEvent
        fields = '__all__'
        exclude = ['user', 'status', 'pay', 'pay_date', 'pay_type', 'reg_code', 'start_number']
        
        
class PayRegEventsForm(forms.ModelForm):
    pay = forms.FloatField(min_value = 0, label = "Оплачена сума", required=True)
    pay_date = forms.DateField(initial = '01.02.2017', input_formats=['%d.%m.%Y'], widget=forms.DateInput(attrs={'id':"pay_datepicker"}, format='%d.%m.%Y'), required=True, label='День оплати')
    pay_time = forms.TimeField(initial = "12:00", input_formats=['%H:%M'], required=True, label='Час оплати')
#    status = forms.BooleanField(label='Статус оплати')
    start_number = forms.IntegerField(label="Стартовий номер", min_value=0, max_value=999, required=False)
    pay_type = forms.ChoiceField(label='Спосіб оплати', choices= RegEvent.PAY_METHOD_CHOICES)
    description = forms.CharField(widget=forms.Textarea(attrs={'cols': 93, 'rows': 8}), required=False, label='Примітки')    
    
    class Meta:
        model = RegEvent
        fields = '__all__'
        exclude = ['user', 'status', 'reg_code', 'event', 'fname', 'lname', 'sex', 'nickname', 'email', 'phone', 'country', 'city', 'club', 'bike_type', 'birthday', 'date']
                    