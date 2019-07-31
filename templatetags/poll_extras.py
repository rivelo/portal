# -*- coding: utf-8 -*-
from django import template
import MySQLdb
from portal.event_calendar.models import Events, ResultEvent, CheckPointEvent
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

import datetime

register = template.Library()
import re


@register.filter
def qr(value,size="120x120"):
    """
        Usage:
        <img src="{{object.code|qr:"120x130"}}" />
    """
    return "http://chart.apis.google.com/chart?chs=%s&cht=qr&chl=%s&choe=UTF-8&chld=H|0" % (size, value)


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


@register.filter(name='get_kp_result')
def get_kp_result(resEvent, kp):
    res = CheckPointEvent.objects.filter(result_event__reg_event__pk = resEvent, number = kp)    
    if res:
        return res.first()
    else:
        return ''

@register.filter(name='kp_test')
def kp_test(kp):
    res = CheckPointEvent.objects.filter(result_event__reg_event__pk = 1495, number = kp)
#    print "REs type = " + str(type(res))
    #print "REs = " + str(res.check_time)
    return res.first().check_time

@register.filter(name='res_statistic')
def res_statistic(event, sex):
    if sex == '1':
        return ResultEvent.male_objects.get_male(event)
    if sex == '0':
        return ResultEvent.female_objects.get_female(event)


@register.filter(name='res_stat_city')
def res_stat_city(event):
        #return ResultEvent.group_city.get_citys(event)
        return ResultEvent.group_city.get_citys(event)

@register.filter(name='res_stat_city_byyear')
def res_stat_city_byyear(year):
        #return ResultEvent.group_city.get_citys(event)
        return ResultEvent.group_city.get_citys_byyear(year)

@register.filter(name='res_stat_bikes')
def res_stat_bikes(event):
        #return ResultEvent.group_city.get_citys(event)
        return ResultEvent.group_bikes.get_bikes(event)

@register.filter(name='res_stat_bikes_byyear')
def res_stat_bikes_byyear(year):
    #return ResultEvent.group_city.get_citys(event)
    return ResultEvent.group_bikes.get_bikes_byyear(year)

def format_timedelta(td):
    hours, remainder = divmod(td.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    hours, minutes, seconds = int(hours), int(minutes), int(seconds)
    if hours < 10:
        hours = '0%s' % int(hours)
    if minutes < 10:
        minutes = '0%s' % minutes
    if seconds < 10:
        seconds = '0%s' % seconds
    return '%s:%s:%s' % (hours, minutes, seconds)
    
@register.simple_tag(name='time_plus_time')
def time_plus_time(time1, time2, time3):
#        time1 = time1
#        time2 = time2
#        time3 = time3
        if time1 == '':
            time1 = '00:00:00'
        if time2 == '':
            time2 = '00:00:00'
        if time3 == '':
            time3 = '00:00:00'
        try:
            a = datetime.datetime.strptime(time1, '%H:%M:%S')
            b = datetime.datetime.strptime(time2, '%H:%M:%S')
            c = datetime.datetime.strptime(time3, '%H:%M:%S')
            adelta = datetime.timedelta(hours=a.hour, minutes=a.minute, seconds=a.second)
            bdelta = datetime.timedelta(hours=b.hour, minutes=b.minute, seconds=b.second)
            cdelta = datetime.timedelta(hours=c.hour, minutes=c.minute, seconds=c.second)
            res = adelta + bdelta + cdelta
        except:
            return 'error' 
        #return str((res.day-1)*24+res.hour)+":"+ str(res.minute) +":"+str(res.second)
        return format_timedelta(res)
#        return res.strftime("%d - %H:%M:%S")

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

@register.simple_tag 
def update_variable_v2(value):
    """Allows to update existing variable in template"""
    return value

@register.filter
def subtract(value, arg):
    return value - arg

@register.simple_tag
def get_filename_icontype(obj, param):
    return obj.get_icon_name(param)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

