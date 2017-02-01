# -*- coding: utf-8 -*-
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
#from portal.news.models import Category

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
        return '%s / %s' % (self.name, self.name_ukr)
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
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    pub_date = models.DateField(auto_now_add=True)
    rules = models.ManyToManyField(Rules, blank=True)
    
    def __unicode__(self):
        return "[%s] - %s" % (self.date, self.name)

    class Meta:
        ordering = ["date"]
    

class RegEvent (models.Model):
    event = models.ForeignKey(Events, blank=True, null=True, on_delete=models.SET_NULL)
    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=150)
    club = models.CharField(max_length=150, blank=True)
    bike_type = models.ForeignKey(BikeType, blank=True, null=True, on_delete=models.SET_NULL)
    birthday = models.DateField(auto_now_add=False, blank = True, null = True)
    pay = models.FloatField(blank = True, null = True)
    date = models.DateTimeField(auto_now_add = True)
    status = models.BooleanField(default=False)
    descriptin = models.TextField(blank=True)

    def __unicode__(self):
        return "%s - [%s]" % (self.fname, self.lname)

    class Meta:
        ordering = ["date"]    
    
    
    
    