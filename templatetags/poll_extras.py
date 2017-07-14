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
#    ev = Events()
    ev = event_res
    #count = ev.r_count(sex)
    a = str("count")
    return a

@register.assignment_tag #(name='minustwo')
def get_current_event():
    c_year = datetime.datetime.now().year
    event = Events.objects.filter(date__year = c_year)
    return event

@register.filter(name='has_group') 
def has_group(user, group_name): 
    group = Group.objects.get(name=group_name) 
    return True if group in user.groups.all() else False
