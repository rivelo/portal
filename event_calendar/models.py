# -*- coding: utf-8 -*-
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
#from portal.news.models import Category

import datetime

# Create your models here.

class EventType(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    
    def __unicode__(self):
        return '%s / %s' % (self.name, self.description)
        #return u'%s - %s' % (self.name, self.name_ukr) 
 
    class Meta:
        ordering = ["name"]    


class Rules(models.Model):
    name = models.CharField(max_length=255)
    date_in = models.DateField()
    date_out = models.DateField()
    sum = models.FloatField(blank = True, null = True)
    description = models.CharField(max_length=255)    
    
    def __unicode__(self):
        return '%s [%s <-> %s] - %s грн.' % (self.name, self.date_in, self.date_out, self.sum)
        #return u'%s - %s' % (self.name, self.name_ukr) 

    class Meta:
        ordering = ["name"]    


class GroupBikeType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    def __unicode__(self):
        return '%s / %s' % (self.name, self.description)
        #return u'%s - %s' % (self.name, self.name_ukr) 

    class Meta:
        ordering = ["name"]    


class BikeType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    group = models.ForeignKey(GroupBikeType, blank=True, null=True, on_delete=models.SET_NULL)
    status = models.BooleanField(default=True)
    
    def __unicode__(self):
        return '%s / %s' % (self.name, self.description)
        #return u'%s - %s' % (self.name, self.name_ukr) 

    class Meta:
        ordering = ["name"]    


class Events (models.Model):
    name = models.CharField(max_length=255)
    type = models.ManyToManyField(EventType, blank=True) # ForeignKey(Type, blank=True, null=True, on_delete=models.SET_NULL)
    text = models.TextField()
    url = models.URLField(max_length=255, blank=True)
    reg_url = models.CharField(max_length=255, blank=True) # registration url
    reg_status = models.BooleanField(default=False)
    photo = models.ImageField(upload_to = 'upload/events/', max_length=255, blank=True, null=True) # poster
    icon = models.ImageField(upload_to = 'upload/events/', max_length=255, blank=True, null=True)
    forum_url = models.URLField(max_length=255, blank=True, null=True)
    gps_track = models.CharField(max_length=255, blank=True) # url to gps   
    #    coordinates
    lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, default=0)
    lng = models.DecimalField(max_digits=9, decimal_places=6, blank=True, default=0)
    city = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date = models.DateTimeField()
    duration = models.PositiveSmallIntegerField(default=1, help_text="тривалість заходу, кількість днів")
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    pub_date = models.DateField(auto_now_add=True)
    rules = models.ManyToManyField(Rules, blank=True)
    
    def save(self, *args, **kwargs):
        if self.reg_status == True:
            self.reg_url = "/event/"+ str(self.pk) +"/registration/"
        super(Events, self).save(*args, **kwargs) # Call the "real" save() method.
    
    def __unicode__(self):
        return u"[%s] - %s" % (self.date, self.name)

    class Meta:
        ordering = ["date"]

from django.core.exceptions import ValidationError    
def validate_phone(value):
    if len(value) < 13 or value[0]<>"+":
        raise ValidationError('%s is not an phone number' % value)


class RegEvent (models.Model):
    PAY_METHOD_CHOICES = (
                          ('card', 'Оплата на картку'),
                          ('shop', 'Оплата в магазині Rivelo'),
                          ('any', 'Інший метод оплати'),
                          )
    SEX_CHOICES = ((1, 'Чоловік'), (0, 'Жінка'))    
    event = models.ForeignKey(Events, blank=True, null=True, on_delete=models.SET_NULL)
    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    sex = models.IntegerField(choices=SEX_CHOICES, help_text="Стать", default=1) # Стать чоловік/жінка
    nickname = models.CharField(max_length=100, help_text="Nickname - Прізвисько", blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=100, validators=[validate_phone])
    country = models.CharField(max_length=100, default="Україна")
    city = models.CharField(max_length=150)
    club = models.CharField(max_length=150, blank=True)
    bike_type = models.ForeignKey(BikeType, blank=True, null=True, on_delete=models.SET_NULL)
    birthday = models.DateField(auto_now_add=False, blank = True, null = True, default=datetime.date(2000,1,1), help_text="Виберіть дату народження: День/Місяць/Рік")
    pay = models.FloatField(blank = True, null = True, help_text=" гривні")
    pay_date = models.DateTimeField(blank = True, null = True)
    pay_type = models.CharField(max_length=50, blank=True, null=True, choices=PAY_METHOD_CHOICES)
    reg_code = models.CharField(max_length=100, blank=True, help_text="Код для можливого редагування ваших даних")
    date = models.DateTimeField(auto_now_add = True)
    status = models.BooleanField(default=False)
    start_number = models.IntegerField(help_text="Стартовий номер", default=0, blank=True) # Стартовий номер; 0 - не вибрано
    description = models.TextField(blank=True)

    def __unicode__(self):
        return u"%s %s - [%s]" % (self.fname, self.lname, self.event)

    class Meta:
        ordering = ["date"]    
    
    
    
    