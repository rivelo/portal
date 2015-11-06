# -*- coding: utf-8 -*-
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User


class Funnies (models.Model):
    RATING_CHOICES = (
        (1, 'Bad'),
        (2, 'Below normal'),
        (3, 'Normal'),
        (4, 'Good'),
        (5, 'Best'),
    )
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(choices = RATING_CHOICES, null = True, blank=True,)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    
    def __unicode__(self):
        return "[%s] - %s" % (self.date, self.text)

    class Meta:
        ordering = ["date"]

