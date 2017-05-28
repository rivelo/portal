# -*- coding: utf-8 -*-
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Count, Sum
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
    
    def cur_date_rule(self):
        today = datetime.date.today()
        if (today >= self.date_in) and (today <= self.date_out):
            return "Діюча вартість на сьогодні " + today.strftime('%d.%m.%Y')
        else:
            return
    
    def __unicode__(self):
        return '%s [%s <-> %s] - %s грн.' % (self.name, self.date_in.strftime('%d.%m.%Y'), self.date_out.strftime('%d.%m.%Y'), self.sum)
        #return u'%s - %s' % (self.name, self.name_ukr) 

    class Meta:
        ordering = ["date_in"]    


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

    def days_left(self):
        today = datetime.datetime.today()
        ldays = (self.date - today).days
        if ldays > 0:
            return ldays
        else:
            return 0

    def riders_count(self, sex=None):
        if sex != None:
            r = self.regevent_set.filter(sex = sex)
        else:
            r = self.regevent_set.all()
        count = r.count()
        return count

    def riders_pay_count(self, pcount=None):
        if pcount == None:
            r = self.regevent_set.filter(status = True)
            count = r.count()
        else:
            r = self.regevent_set.filter(status=True).aggregate(total_pay=Sum('pay'))
            count = r.values()[0]
        return count

    def riders_pay_sum(self):
         r = self.regevent_set.filter(status=True).aggregate(total_pay=Sum('pay'))
         psum = r.values()[0]
         return psum

    def riders_city(self):
        r = self.regevent_set.values('city').annotate(num_city=Count('city')).order_by('-num_city')
        return r

    def riders_bike(self):
        r = self.regevent_set.values('bike_type', 'bike_type__name').annotate(num_bike=Count('bike_type')).order_by('-num_bike')
        return r

    def cur_reg_sum(self, today=datetime.date.today()):
        #today = datetime.date.today()
        rule = self.rules.get(date_in__lte = today, date_out__gte = today)
#        if (today >= self.date_in) and (today <= self.date_out):
        return rule.sum
    
    def save(self, *args, **kwargs):
#        if self.reg_status == True:
#            self.reg_url = "/event/"+ str(self.pk) +"/registration/"
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
    pay_date = models.DateTimeField(blank = True, null = True )
    pay_type = models.CharField(max_length=50, blank=True, null=True, choices=PAY_METHOD_CHOICES)
    reg_code = models.CharField(max_length=100, blank=True, help_text="Код для можливого редагування ваших даних")
    date = models.DateTimeField(auto_now_add = True)
    status = models.BooleanField(default=False)
    start_number = models.IntegerField(help_text="Стартовий номер від 1 до 999", default=0, blank=True) # Стартовий номер; 0 - не вибрано
    description = models.TextField(blank=True)
    #start_status = models.BooleanField(default=False)

    def category(self):
        event_date = self.event.date
        birthday = self.birthday

        cat0_b = event_date.replace(year = event_date.year-12)
        cat0_e = event_date.replace(year = event_date.year-18)
        if (birthday <= cat0_b.date()) and (birthday >= cat0_e.date()): 
            return 0
        
        cat1_b = event_date.replace(year = event_date.year-18)
        cat1_e = event_date.replace(year = event_date.year-30)
        if (birthday <= cat1_b.date()) and (birthday >= cat1_e.date()):
            return 1
        
        cat2_b = event_date.replace(year = event_date.year-30)
        cat2_e = event_date.replace(year = event_date.year-40)
        if (birthday <= cat2_b.date()) and (birthday >= cat2_e.date()):
            return 2
        
        cat3_b = event_date.replace(year = event_date.year-40)
        cat3_e = event_date.replace(year = event_date.year-50)
        if (birthday <= cat3_b.date()) and (birthday >= cat3_e.date()):
            return 3
        
        cat4_b = event_date.replace(year = event_date.year-50)
        cat4_e = event_date.replace(year = event_date.year-60)
        if (birthday <= cat4_b.date()) and (birthday >= cat4_e.date()):
            return 4

        cat5_b = event_date.replace(year = event_date.year-60)
        #revent_cat5 = RegEvent.objects.filter(event = id, birthday__lte = cat5_b).order_by("date") #all rider list
        if (birthday <= cat5_b.date()):
            return 5
 

    def save(self, *args, **kwargs):
#        if self.reg_status == True:
#            self.reg_url = "/event/"+ str(self.pk) +"/registration/"
        super(RegEvent, self).save(*args, **kwargs) # Call the "real" save() method.

    def __unicode__(self):
        return u"%s %s - [%s]" % (self.fname, self.lname, self.event)

    class Meta:
        ordering = ["date"]    


#===============================================================================
# class PointType(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.TextField(blank=True)
#     event = models.ForeignKey(Events, blank=True, null=True, on_delete=models.SET_NULL)
#     status = models.BooleanField(default=True)
#     
#     def __unicode__(self):
#         return '%s / %s' % (self.name, self.description)
#         #return u'%s - %s' % (self.name, self.name_ukr) 
# 
#     class Meta:
#         ordering = ["name"]        
#     
#===============================================================================
    
#===============================================================================
# class ResultEvent (models.Model):
#     reg_event = models.ForeignKey(RegEvent, blank=True, null=True, on_delete=models.SET_NULL)    
# #    point_type = models.ForeignKey(PointType, blank=True, null=True, on_delete=models.SET_NULL)
#     start = models.DateTimeField(blank = True, null = True)
#     kp1 = models.DateTimeField(blank = True, null = True)
#     kp2 = models.DateTimeField(blank = True, null = True)
#     kp3 = models.DateTimeField(blank = True, null = True)
#     finish = models.DateTimeField(blank = True, null = True)
#     description = models.TextField(blank=True)
# 
#     def save(self, *args, **kwargs):
# #        if self.reg_status == True:
# #            self.reg_url = "/event/"+ str(self.pk) +"/registration/"
#         super(ResultEvent, self).save(*args, **kwargs) # Call the "real" save() method.
# 
#     def __unicode__(self):
#         return u"%s %s - [%s]" % (self.point_type, self.dtime, self.description)
# 
#     class Meta:
#         ordering = ["reg_event", "dtime"]    
#     
#===============================================================================

    
    