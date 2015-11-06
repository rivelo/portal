# -*- coding: utf-8 -*-

# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpRequest, HttpResponseNotFound
from django.conf import settings


def custom_proc(request):
# "A context processor that provides 'app', 'user' and 'ip_address'."
    return {
        'app': 'Rivelo catalog',
        'user': request.user,
        'ip_address': request.META['REMOTE_ADDR']
    }


def gallery_page(request):
    return render_to_response('index.html', {'weblink': 'photo.html', 'sel_menu': 'photo'}, context_instance=RequestContext(request, processors=[custom_proc]))
