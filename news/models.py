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
    link = models.URLField(verify_exists=False)
    author = models.CharField(max_length=50)
    category = models.ForeignKey(Category)
    comments = models.ManyToManyField(Comments)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    
    def __unicode__(self):
        return self.text

    class Meta:
        ordering = ["date"]    
