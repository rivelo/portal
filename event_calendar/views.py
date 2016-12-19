# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpRequest, HttpResponseNotFound
from django.conf import settings
import datetime, calendar

from portal.mysql_portal import get_month_event, get_month_events, get_day_events


def custom_proc(request):
# "A context processor that provides 'app', 'user' and 'ip_address'."
    return {
        'app': 'Rivelo catalog',
        'user': request.user,
        'ip_address': request.META['REMOTE_ADDR']
    }


def move_month(date, delta=1):
    m = date.month + delta - 1
    res = datetime.date( (date.year * 12 + m) // 12 , m % 12 + 1 , date.day )
    return res


def embeded_calendar(year=datetime.date.today().year, month = datetime.date.today().month):
    year = int(year)
    month = int(month)
    today = datetime.date.today().day
    selected_date = datetime.date(year, month, today)
    
    month_calendar = calendar.monthcalendar(year, month)
    next_date = move_month(datetime.date(year, month, 1), 1)
    prev_date = move_month(datetime.date(year, month, 1), -1)

    month_events = get_month_events(year, month)

    return {'weeks': month_calendar, 'events': get_month_event(year, month),
            'sel_day': today, 'sel_date': selected_date, 
            'prev_month': prev_date, 'next_month': next_date, 'month_events': month_events } 
    
    
def calendar_page(request):
    return render_to_response('index.html', {'weblink': 'event_list.html', 'sel_menu': 'event'}, context_instance=RequestContext(request, processors=[custom_proc]))

