# -*- coding: utf-8 -*-
from django import template
import MySQLdb
from portal.event_calendar.models import Events

import datetime

register = template.Library()
import re


@register.filter(name='inday')
def inday(value, arg):
    if arg in value:
        return value[arg]
    else:
        return None


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


@register.assignment_tag #(name='minustwo')
def get_current_event():
    c_year = datetime.datetime.now().year
    event = Events.objects.filter(date__year = c_year)
    return event