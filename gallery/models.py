# -*- coding: utf-8 -*-
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User


class Album(models.Model):
    title = models.CharField(max_length=100)
    url = models.URLField(unique=True)
    numphotos = models.IntegerField(blank=True, null=True)
    album_id = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return self.url

    class Meta:
        ordering = ('title',)

class PhotoManager(models.Manager):
    def get_queryset(self):
        return super(PhotoManager, self).get_queryset().all()

    def random(self):
        return self.get_queryset().order_by('?')[:1][0]

class Photo(models.Model):
    album = models.ForeignKey(Album)
    title = models.CharField(max_length=100)
    image = models.URLField()
    url = models.URLField(unique=True)
    pub_date = models.DateTimeField("Publication date", blank=True, null=True)
    filename = models.CharField(max_length=100)
    photo_id = models.CharField(max_length=255, unique=True)
    height = models.IntegerField(blank=True, null=True)
    width = models.IntegerField(blank=True, null=True)

    objects = PhotoManager()

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return self.url

    class Meta:
        ordering = ('album', 'title')
        get_latest_by = 'pub_date'