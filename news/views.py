# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpRequest, HttpResponseNotFound
from django.conf import settings

from portal.event_calendar.views import embeded_calendar
from portal.funnies.views import get_funn
from models import News
from portal.gallery.models import Album, Photo

def custom_proc(request):
# "A context processor that provides 'app', 'user' and 'ip_address'."
    return {
        'app': 'Rivelo catalog',
        'user': request.user,
        'ip_address': request.META['REMOTE_ADDR']
    }

    
def auth_group(user, group):
    return True if user.groups.filter(name=group) else False



def main_page(request):
    #return HttpResponse("Hello world")
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'main.html', 'sel_menu': 'main', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn()}
    calendar = embeded_calendar()
    vars.update(calendar)
    
    return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))

def contact_page(request):
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'contact.html', 'sel_menu': 'contact', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn()}
    calendar = embeded_calendar()
    vars.update(calendar)
    
    return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))

def about_page(request):
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'about.html', 'sel_menu': 'about', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn()}
    calendar = embeded_calendar()
    vars.update(calendar)
    
    return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))
    
    
from django.views.decorators.csrf import csrf_protect
from django.contrib import auth 

def login(request):
    message = "AJAX"
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('user'):
                user = request.POST.get('user')
            if POST.has_key('password'):
                password = request.POST.get('password')
            user = auth.authenticate(username=user, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponse(simplejson.dumps({'response': message, 'result': 'success'}))
            else:
                return HttpResponse(simplejson.dumps({'response': message, 'result': 'error'}))
        
    username = request.POST['username']
    password = request.POST['password']
    next = request.POST['next']
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        # Правильный пароль и пользователь "активен"
        auth.login(request, user)
        # Перенаправление на "правильную" страницу
        if next:
            return HttpResponseRedirect(next)
        else:
            return HttpResponseRedirect("/.")            
    else:
        # Отображение страницы с ошибкой
        
            #return HttpResponse(simplejson.dumps(TheStory), mimetype="application/json")
        if next:
            return HttpResponseRedirect(next)
        else:
            return HttpResponseRedirect("/.")            


def logout(request):
    auth.logout(request)
    next_page = request.POST['next_page']
    # Перенаправление на страницу.
    if next_page:
        #return HttpResponseRedirect(next_page)
        return HttpResponseRedirect("/.")
    else:
        return HttpResponseRedirect("/.")
    
