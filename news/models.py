# -*- coding: utf-8 -*-

from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    locality = models.CharField(max_length=30)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]    


class Comments(models.Model):
    text = models.TextField()
    date = models.DateTimeField()
    username = models.CharField(max_length=50)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    
    def __unicode__(self):
        return "[%s] - %s" % (self.date, self.text)

    class Meta:
        ordering = ["date", "user"]    


class News(models.Model):
    title = models.CharField(max_length=255) 
    text = models.TextField()
    date = models.DateTimeField()
    link = models.URLField()
    author = models.CharField(max_length=50)
    category = models.ForeignKey(Category)
    comments = models.ManyToManyField(Comments, blank=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    img_url = models.CharField(max_length=255, blank=True, null=True)
    #url_desc = models.TextField(blank=True, null=True) # положення до заходу
    
    def __unicode__(self):
        return self.text

    class Meta:
        ordering = ["date"]    


class Route(models.Model):
    title = models.CharField(max_length=255) 
    description = models.TextField(blank = True, null = True)
    year = models.PositiveSmallIntegerField()
    gpsies = models.CharField(blank=True, null = True, max_length=255)
    comments = models.ManyToManyField(Comments, blank=True)
    ranking = models.FloatField(default = 0)
    level = models.PositiveIntegerField() # Рівень підготовки
    season = models.CharField(blank=True, null = True, max_length=255) 
    bike_type = models.CharField(blank=True, null = True, max_length=255) 
    duration = models.DurationField(default = 0)
    distance = models.PositiveSmallIntegerField()
    photo_google = models.CharField(blank=True, null = True, max_length=255)
    
    def __unicode__(self):
        return u'%s - %s рік' % (self.title, self.year) 

    class Meta:
        ordering = ["level"]    
