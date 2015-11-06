# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpRequest, HttpResponseNotFound
from django.conf import settings

from rivelo_portal.event_calendar.views import embeded_calendar
from models import Funnies


def custom_proc(request):
# "A context processor that provides 'app', 'user' and 'ip_address'."
    return {
        'app': 'Rivelo catalog',
        'user': request.user,
        'ip_address': request.META['REMOTE_ADDR']
    }


def get_funn(id):
    try:
        f = Funnies.objects.get(id = id)
    except:
        f = Funnies.objects.none()
    return f.text