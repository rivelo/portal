# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpRequest, HttpResponseNotFound
from django.conf import settings

#from portal.event_calendar.views import embeded_calendar
from models import Funnies


def custom_proc(request):
# "A context processor that provides 'app', 'user' and 'ip_address'."
    return {
        'app': 'Rivelo catalog',
        'user': request.user,
        'ip_address': request.META['REMOTE_ADDR']
    }


def get_funn(id=None):
    if id == None:
        try:
            f = Funnies.objects.all().order_by('?')[:1].get()
        except:
            return ''
    else:
        try:
            f = Funnies.objects.get(id = id)
        except:
            return ''
    return f.text