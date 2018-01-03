# -*- coding: utf-8 -*-
from django import template
import MySQLdb
from portal.event_calendar.models import Events, ResultEvent
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

import datetime

register = template.Library()
import re


@register.filter(name='inday')
def inday(value, arg):
    if arg in value:
        return value[arg]
    else:
        return None

@register.filter
def lower1(value): # Only one argument.
    """Converts a string into all lowercase"""
    return value.lower()

@register.filter(name='season')
def season(value):
    name = ('winter','spring','summer','autumn')
    p = datetime.datetime.now().month % 12 / 3
    str = value + "logo_" + name[p] + ".gif" 
    return str

@register.filter(name='rider_statistic')
def rider_statistic(event, sex):
#    ev = Events()
    ev = event
    count = ev.riders_count(sex)
    a = str(count)
    return a

@register.filter(name='res_statistic')
def res_statistic(event_res, sex):
    count = event_res.riders_count(sex)
    return count

@register.assignment_tag #(name='minustwo')
def get_current_event():
    c_year = datetime.datetime.now().year
    event = Events.objects.filter(date__year = c_year)
    return event

@register.assignment_tag #(name='minustwo')
def get_archive_event():
    c_year = datetime.datetime.now().year
    cn = datetime.datetime(c_year, 1, 1)
     #now-datetime.timedelta(days=360)
    event = Events.objects.filter(date__lt=cn).order_by('date') # date__year__lte = c_year).order_by('date')
    return event

@register.assignment_tag #(name='minustwo')
def get_current_year():
    c_year = datetime.datetime.now().year
    return c_year

@register.filter(name='has_group') 
def has_group(user, group_name): 
    group = Group.objects.get(name=group_name) 
    return True if group in user.groups.all() else False

@register.assignment_tag
def update_variable(value):
    """Allows to update existing variable in template"""
    return value
