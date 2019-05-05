# -*- coding: utf-8 -*-

from pyexpat import model

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


class Events(models.Model):
    name = models.CharField(max_length=255)
    type = models.ManyToManyField(EventType, blank=True) # ForeignKey(Type, blank=True, null=True, on_delete=models.SET_NULL)
    text = models.TextField()
    #evnt_rules = models.TextField()
    #text_invite = models.TextField()
    url = models.URLField(max_length=255, blank=True)
    reg_url = models.CharField(max_length=255, blank=True) # registration url
    reg_status = models.BooleanField(default=False)
    photo = models.ImageField(upload_to = 'upload/events/', max_length=255, blank=True, null=True) # poster
    icon = models.ImageField(upload_to = 'upload/events/', max_length=255, blank=True, null=True)
    forum_url = models.URLField(max_length=255, blank=True, null=True)
    #facebook_url = models.URLField(max_length=255, blank=True, null=True)
    gps_track = models.CharField(max_length=255, blank=True) # url to gps   
    #    coordinates
    lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, default=0)
    lng = models.DecimalField(max_digits=9, decimal_places=6, blank=True, default=0)
    city = models.CharField(max_length=100)
    description = models.TextField(blank=True) # положення 
    date = models.DateTimeField()
    duration = models.PositiveSmallIntegerField(default=1, help_text="тривалість заходу, кількість днів")
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    pub_date = models.DateField(auto_now_add=True)
    rules = models.ManyToManyField(Rules, blank=True) #реєстраційні внески
    email_text = models.TextField(blank=True)
    cup = models.BooleanField(default=False)

    def days_left(self):
        today = datetime.datetime.today()
        ldays = (self.date - today).days + 1
        if ldays > 0:
            return ldays
        else:
            return 0

    def real_day_left(self):
        today = datetime.datetime.today()
        ldays = (self.date - today).days + 1
        return ldays

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

    def riders_pay_sum_card(self):
         r = self.regevent_set.filter(status=True, pay_type='card').aggregate(total_pay=Sum('pay'))
         psum = r.values()[0]
         return psum

    def riders_pay_sum_shop(self):
         r = self.regevent_set.filter(status=True, pay_type='shop').aggregate(total_pay=Sum('pay'))
         psum = r.values()[0]
         return psum

    def riders_pay_sum_other(self):
         r = self.regevent_set.filter(status=True, pay_type='any').aggregate(total_pay=Sum('pay'))
         psum = r.values()[0]
         return psum

    def riders_city(self):
        r = self.regevent_set.values('city').annotate(num_city=Count('city')).order_by('-num_city')
        return r

    def riders_bike(self):
        r = self.regevent_set.values('bike_type', 'bike_type__name').annotate(num_bike=Count('bike_type')).order_by('-num_bike')
        return r

    def cur_reg_sum(self, today=datetime.date.today):
        #today = datetime.date.today()
        try:
            rule = self.rules.get(date_in__lte = today, date_out__gte = today)
        except:
            today=datetime.date.today()
            try:
                rule = self.rules.get(date_in__lte = today, date_out__gte = today)
            except:
                rule = "Час реєстрації вичерпався, тому відправляти лист або реєструватись вже не доречно"
                return ("error", rule) 
            #rule = 0
        #    return 0
#        if (today >= self.date_in) and (today <= self.date_out):
        return rule.sum

    def result_present(self):
        res = ResultEvent.objects.filter(reg_event__event = self.pk)
        if res:
            return True
        else: 
            return False
    
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


class EventDistance(models.Model):
    name = models.CharField(max_length=255)
    distance = models.PositiveSmallIntegerField(default=0, help_text="Довжина маршруту, кілометри")
    event = models.ForeignKey(Events, blank=True, null=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True, help_text="Опис дистанції")

    def __unicode__(self):
        return '%s - %s км' % (self.name, self.distance)

    class Meta:
        ordering = ["event", "distance", "name"]    


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
    #chip_number = models.CharField IntegerField(help_text="номер чіпа", default=0, blank=True) # Стартовий номер; 0 - не вибрано
    distance_type = models.ForeignKey(EventDistance, blank=True, null=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True)
    start_status = models.BooleanField(default=False)

    def category(self):
        event_date = self.event.date
        birthday = self.birthday

        cat0_b = event_date.replace(year = event_date.year-12)
        cat0_e = event_date.replace(year = event_date.year-18)
        if (birthday <= cat0_b.date()) and (birthday >= cat0_e.date()): 
            return [0, u'до 18 років']
        
        cat1_b = event_date.replace(year = event_date.year-18)
        cat1_e = event_date.replace(year = event_date.year-30)
        if (birthday <= cat1_b.date()) and (birthday >= cat1_e.date()):
            #return 1
            return [1, u'18-29 років']
        
        cat2_b = event_date.replace(year = event_date.year-30)
        cat2_e = event_date.replace(year = event_date.year-40)
        if (birthday <= cat2_b.date()) and (birthday >= cat2_e.date()):
            #return 2
            return [2, u'30-39 років']
        
        cat3_b = event_date.replace(year = event_date.year-40)
        cat3_e = event_date.replace(year = event_date.year-50)
        if (birthday <= cat3_b.date()) and (birthday >= cat3_e.date()):
            #return 3
            return [3, '40-49 років']
        
        cat4_b = event_date.replace(year = event_date.year-50)
        cat4_e = event_date.replace(year = event_date.year-60)
        if (birthday <= cat4_b.date()) and (birthday >= cat4_e.date()):
            #return 4
            return [4, '50-59 років']

        cat5_b = event_date.replace(year = event_date.year-60)
        #revent_cat5 = RegEvent.objects.filter(event = id, birthday__lte = cat5_b).order_by("date") #all rider list
        if (birthday <= cat5_b.date()):
            #return 5
            return [5, u'60+ років']
 
    def get_pos(self):
        
        return None 

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
'''class SexManager(models.Manager):
     def riders_count(self):
        sex = 1
        if sex != None:
            r = self.regevent_set.filter(sex = sex)
        else:
            r = self.regevent_set.all()
        count = r.count()
        return count
'''
class MaleManager(models.Manager):
    def get_queryset(self):
        return super(MaleManager, self).get_queryset().filter(reg_event__sex=1).count()

    def get_male(self, event):
        return super(MaleManager, self).get_queryset().filter(reg_event__sex=1, reg_event__event__pk=event).count()

    def get_male_byyear(self, year):
        return super(MaleManager, self).get_queryset().filter(reg_event__sex=1, reg_event__event__date__year = year).count()

class FemaleManager(models.Manager):
    def get_queryset(self):
        return super(FemaleManager, self).get_queryset().filter(reg_event__sex=0).count()

    def get_female(self, event):
        return super(FemaleManager, self).get_queryset().filter(reg_event__sex=0, reg_event__event__pk=event).count()

    def get_female_byyear(self, year):
        return super(FemaleManager, self).get_queryset().filter(reg_event__sex=0, reg_event__event__date__year = year).count()


class CityManager(models.Manager):
    def get_citys(self, event):
        return super(CityManager, self).get_queryset().filter(reg_event__event__pk = event).values('reg_event__city').annotate(num_city=Count('reg_event__city')).order_by('-num_city')

    def get_citys_byyear(self, year):
        return super(CityManager, self).get_queryset().filter(reg_event__event__date__year = year).values('reg_event__city').annotate(num_city=Count('reg_event__city')).order_by('-num_city')


class BikesManager(models.Manager):
    def get_bikes(self, event):
        return super(BikesManager, self).get_queryset().filter(reg_event__event__pk = event).values('reg_event__bike_type__name').annotate(num_bike=Count('reg_event__bike_type')).order_by('-num_bike')

    def get_bikes_byyear(self, year):
        return super(BikesManager, self).get_queryset().filter(reg_event__event__date__year = year).exclude(finish__isnull=True).values('reg_event__bike_type__name').annotate(num_bike=Count('reg_event__bike_type')).order_by('-num_bike')


class CustomQuerySetManager(models.Manager):
    """A re-usable Manager to access a custom QuerySet"""
    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            # don't delegate internal methods to the queryset
            if attr.startswith('__') and attr.endswith('__'):
                raise
            return getattr(self.get_query_set(), attr, *args)

    def get_query_set(self):
        return self.model.QuerySet(self.model, using=self._db)
    
class filterManager(models.Manager):
  def get_queryset(self):
      return super(filterManager, self).get_query_set().all()#filter(name='troy')

from django.db.models.query import QuerySet

#    class QuerySet(QuerySet):
class GroupQuerySet(QuerySet):        
    def active_for_account(self, sex, *args, **kwargs):
        return self.filter(reg_event__sex=sex) #filter(account=account, deleted=False, *args, **kwargs)
 
    def get_sex(self, sex=0, *args, **kwargs):
        return self.filter(reg_event__sex=sex).count()

    def group_city(self, *args, **kwargs):
        return self.values('reg_event__city').annotate(num_city=Count('reg_event__city')).order_by('-num_city')

    def group_bike(self, *args, **kwargs):
        return self.values('reg_event__bike_type__name').annotate(num_bike=Count('reg_event__bike_type')).order_by('-num_bike')
    
class ResultEvent (models.Model):
    reg_event = models.ForeignKey(RegEvent, blank=True, null=True, on_delete=models.SET_NULL)    
#    point_type = models.ForeignKey(PointType, blank=True, null=True, on_delete=models.SET_NULL)
    start = models.DateTimeField(blank = True, null = True)
    kp1 = models.DateTimeField(blank = True, null = True)
    kp2 = models.DateTimeField(blank = True, null = True)
    kp3 = models.DateTimeField(blank = True, null = True)
    finish = models.DateTimeField(blank = True, null = True)
    description = models.TextField(blank=True)
    dnf = models.BooleanField(default=False)
#    objects = filterManager()
    #objects = CustomQuerySetManager()
    objects = models.Manager() # The default manager.
    male_objects = MaleManager() # The specific manager.
    female_objects = FemaleManager() 
    group_city = CityManager()
#    people = CustomManager()
    group_bikes = BikesManager()
    #p_groups = GroupQuerySet.as_manager()

    def get_time_diff(self):
        if self.start == None:
            return "DNS"
        if self.finish == None:
            return "DNF"
        res = self.finish - self.start
        return str(res)   # Assuming dt2 is the more recent time

    def get_time_diff_kp1(self):
        if self.start == None:
            return "DNS"
        if self.kp1 == None:
            return ""
        res = self.kp1 - self.start
        return str(res)   # Assuming dt2 is the more recent time

    def get_time_diff_kp2(self):
        if self.start == None:
            return "DNS"
        if self.kp2 == None:
            return ""
        res = self.kp2 - self.kp1
        return str(res)   # Assuming dt2 is the more recent time

   
#    def riders_city(self):
#        r = self.regevent_set.values('city').annotate(num_city=Count('city')).order_by('-num_city')
#        return r
 
    def save(self, *args, **kwargs):
#        if self.reg_status == True:
#            self.reg_url = "/event/"+ str(self.pk) +"/registration/"
        super(ResultEvent, self).save(*args, **kwargs) # Call the "real" save() method.
 
    def __unicode__(self):
        return u"%s - [%s]" % (self.reg_event, self.finish)

    class QuerySet(QuerySet):
    #class GroupQuerySet(QuerySet):        
        def active_for_account(self, sex, *args, **kwargs):
            return self.filter(reg_event__sex=sex) #filter(account=account, deleted=False, *args, **kwargs)
 
        def get_sex(self, sex=0, *args, **kwargs):
            return self.filter(reg_event__sex=sex).count()

        def group_city(self, *args, **kwargs):
            return self.values('reg_event__city').annotate(num_city=Count('reg_event__city')).order_by('-num_city')

        def group_bike(self, *args, **kwargs):
            return self.values('reg_event__bike_type__name').annotate(num_bike=Count('reg_event__bike_type')).order_by('-num_bike')

 
    class Admin:
        manager = filterManager()
 
    class Meta:
        ordering = ["reg_event", "finish"]    
     

    
    