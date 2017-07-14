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
    time = forms.TimeField(initial = "10:00", input_formats=['%H:%M'], required=False)
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

    def clean(self):
        cleaned_data = super(RegEventsForm, self).clean()
        chk_phone = cleaned_data.get("phone")
        chkevent = cleaned_data.get("event")
        chkcity = cleaned_data.get("city")
        res = RegEvent.objects.filter(event = chkevent, phone = chk_phone)
        if res :
            raise forms.ValidationError("Користувач з таким телефоном вже існує")
        if chkcity == '':
            raise forms.ValidationError("Виберіть місто з автодоповнення")
        # Always return the full collection of cleaned data.
        return cleaned_data

    class Meta:
        model = RegEvent
        fields = '__all__'
        exclude = ['user', 'status', 'pay', 'pay_date', 'pay_type', 'reg_code', 'start_number']
        

def auth_group(user, group):
    return True if user.groups.filter(name=group) else False        
        
class PayRegEventsForm(forms.ModelForm):
    pay = forms.FloatField(min_value = 0, label = "Оплачена сума", required=True)
    pay_date = forms.DateField(initial = '01.02.2017', input_formats=['%d.%m.%Y'], widget=forms.DateInput(attrs={'id':"pay_datepicker"}, format='%d.%m.%Y'), required=True, label='День оплати')
    pay_time = forms.TimeField(initial = "12:00", input_formats=['%H:%M'], required=True, label='Час оплати')
#    status = forms.BooleanField(label='Статус оплати')
    start_number = forms.IntegerField(label="Стартовий номер", min_value=0, max_value=999, required=False)
    pay_type = forms.ChoiceField(label='Спосіб оплати', choices= RegEvent.PAY_METHOD_CHOICES)
    description = forms.CharField(widget=forms.Textarea(attrs={'cols': 93, 'rows': 8}), required=False, label='Примітки')    

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(PayRegEventsForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(PayRegEventsForm, self).clean()
        chk_number = cleaned_data.get("start_number")
        chk_pay = cleaned_data.get("pay")
        pdate = cleaned_data.get("pay_date")
        person_id = cleaned_data.get("person_id")
        if not pdate:
            msg = "Введіть дату і час коли була здійснена оплата"
            self._errors["pay_date"] = self.error_class([msg])
            raise forms.ValidationError("Відсутня ДАТА або ЧАС")
        chk_event = self.instance.event
        sum = chk_event.cur_reg_sum(pdate)
        try:
            cpay = int(chk_pay)
            if int(chk_pay) <= sum-1 and auth_group(self.request.user, 'admin')==False:
                msg = "Ваша оплата менша за стартовий внесок %s гривень на %s " % (chk_event.cur_reg_sum(pdate), pdate.strftime('%d.%m.%Y'))
                self._errors["pay"] = self.error_class([msg])
        except:
            msg = "Введіть суму оплати"
            self._errors["pay"] = self.error_class([msg])
        
#        if auth_group(self.request.user, 'admin')==True:
#            msg = forms.ValidationError("%s - %s" % ("У вас не достатньо повноважень", self.request.user)) 
#            self._errors["pay"] = self.error_class([msg])

            #raise forms.ValidationError("Ваша оплата менша за стартовий внесок %s гривень на %s " % (chk_event.cur_reg_sum(pdate), pdate.strftime('%d.%m.%Y')))             
        #res = RegEvent.objects.filter(event = chk_event, start_number__gt=0).order_by('start_number')
        res = RegEvent.objects.filter(event = chk_event, start_number__gt=0).values_list('start_number', flat=True).order_by('start_number')
        if len(res) > 0 :
            nlist = ', '.join(map(str, res))
            if chk_number in res:
                #del cleaned_data["start_number"]
                raise forms.ValidationError("Номер %s вже вибраний. Виберіть інший окрім (%s)" % (chk_number, nlist))
        # Always return the full collection of cleaned data.
        return cleaned_data

    
    class Meta:
        model = RegEvent
        fields = '__all__'
        exclude = ['user', 'status', 'reg_code', 'event', 'fname', 'lname', 'sex', 'nickname', 'email', 'phone', 'country', 'city', 'club', 'bike_type', 'birthday', 'date']
                    