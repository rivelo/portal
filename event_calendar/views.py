# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpRequest, HttpResponseNotFound
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
import datetime, calendar

from models import Events
from forms import EventsForm

from portal.gallery.models import Album, Photo
from portal.funnies.views import get_funn

import simplejson
import googlemaps

from portal.mysql_portal import get_month_event, get_month_events, get_day_events


def custom_proc(request):
# "A context processor that provides 'app', 'user' and 'ip_address'."
    return {
        'app': 'Rivelo catalog',
        'user': request.user,
        'ip_address': request.META['REMOTE_ADDR']
    }


def processUploadedImage(file, dir=''): 
    upload_suffix = 'upload/' + dir + file.name
    upload_path = settings.MEDIA_ROOT + 'upload/' + file.name
        
    destination = open(settings.MEDIA_ROOT + '/upload/'+ dir + file.name, 'wb+')
    #destination = open('/media/upload/'+file.name, 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()        
    return upload_suffix


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

    #month_events = get_month_events(year, month)
    
    events = Events.objects.filter(date__year = year).order_by('date').values("name", "text", "type", "icon", "date")
    str = ""
    list = []
    for i in events:
        str = str +"'"+ i['date'].strftime('%d-%m-%Y')+"',"
        list.append(i['date'].strftime('%d-%m-%Y'))

    return {'weeks': month_calendar, 'events': get_month_event(year, month),
            'sel_day': today, 'sel_date': selected_date, 
            'prev_month': prev_date, 'next_month': next_date, 'year': year, 'events_date': list} 
#            'prev_month': prev_date, 'next_month': next_date, 'month_events': month_events , 'year': year, 'events_date': list}
    
    
def calendar_page(request):
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    calendar = embeded_calendar()
    vars = {'weblink': 'event_list.html', 'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn()}
    calendar = embeded_calendar()
    vars.update(calendar)    
    events = Events.objects.all().order_by('date')
    evnt = {'events': events}
    vars.update(evnt)
    return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))


def calendar_filter(request, year, month=None):
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    calendar = embeded_calendar()
    vars = {'weblink': 'event_list.html', 'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn()}
    calendar = embeded_calendar()
    vars.update(calendar)    
    if month == None:
        events = Events.objects.filter(date__year = year).order_by('date')
    else:
        events = Events.objects.filter(date__year = year, date__month = month).order_by('date')
    evnt = {'events': events}
    vars.update(evnt)
    return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))


def google_location(request):
    gmaps = googlemaps.Client(key='AIzaSyDR8YRTxz9xNV1F75RQp1IwKA4Dt6MBUKQ')
    res = gmaps.places_autocomplete("кост", language="ua", type='(regions)', components={'country': 'ua'})
    str = "<br>"
    for i in res:
        str = str + i['terms'][0]['value']+ " / " + i['description'] + "<br>"  
#    return HttpResponse("Список міст:" + res[0]['terms'][0]['value'])
    return HttpResponse("<b>Список міст:</b>" + str)


def get_event(request):
#    date_before = datetime.datetime.today() - datetime.timedelta(days=180)
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('dates'):
                d = request.POST['dates']
                date_y = int(d[6:])
                date_m = int(d[3:5])
                date_d = int(d[:2])
                elist = Events.objects.filter(date__year = date_y, date__month = date_m, date__day = date_d).values("name", "text", "type", "icon", "date", "photo", "user__username", "pub_date")
                json = list(elist)
                for x in json:  
                    x['date'] = x['date'].strftime("%d/%m/%Y")
                    x['pub_date'] = x['pub_date'].strftime("%d/%m/%Y")
                #json = serializers.serialize('json', p_cred_month, fields=('id', 'date', 'price', 'description', 'user', 'user_username'))
                return HttpResponse(simplejson.dumps(json), content_type='application/json')
    
    return HttpResponse(elist, content_type='application/json')        


from django.contrib.auth.models import User

def add_event(request):
    if request.user.is_authenticated()==False:
        return HttpResponse("<h2>Для виконання операції, авторизуйтесь</h2>")
    a = Events()
    if request.method == 'POST':
        form = EventsForm(request.POST, instance=a)
        if form.is_valid():
            name = form.cleaned_data['name']
            type = form.cleaned_data['type']
            text = form.cleaned_data['text']
            url = form.cleaned_data['url']
            reg_url = form.cleaned_data['url']
            reg_status = form.cleaned_data['reg_status']
            photo = form.cleaned_data['photo']
            icon = form.cleaned_data['icon']
            forum_url = form.cleaned_data['forum_url']
            gps_track = form.cleaned_data['gps_track']
            lat = form.cleaned_data['lat']
            lng = form.cleaned_data['lng']
            city = form.cleaned_data['city']
            description = form.cleaned_data['description']
            date = form.cleaned_data['date']
            user = request.user
            if lat == None:
                lat = 0 
            if lng == None:
                lng = 0 
                
            evt = Events(name=name, text=text, url=url, reg_url=reg_url, reg_status=reg_status, photo=photo, icon=icon, forum_url=forum_url, lat=lat, lng=lng, description=description, date=date, user = user)
            evt.save()
            for t in type: 
                evt.type.add(t)
            evt.save()
            return HttpResponseRedirect('/calendar/')
    else:
        form = EventsForm(instance=a)
    #return render_to_response('bank.html', {'form': form})
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'event_add.html', 'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'form': form}
    calendar = embeded_calendar()
    vars.update(calendar)        
    events = Events.objects.all().order_by('date')
    evnt = {'events': events}
    vars.update(evnt)
    return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))    
    

def edit_event(request, id):
    if request.user.is_authenticated()==False:
        return HttpResponse("<h2>Для виконання операції, авторизуйтесь</h2>")
    a = Events.objects.get(pk=id)
    if request.method == 'POST':
        form = EventsForm(request.POST, request.FILES, instance=a)
        if form.is_valid():
            name = form.cleaned_data['name']
            type = form.cleaned_data['type']
            text = form.cleaned_data['text']
            url = form.cleaned_data['url']
            reg_url = form.cleaned_data['url']
            reg_status = form.cleaned_data['reg_status']
            photo = form.cleaned_data['photo']
            if photo == None:
                upload_path_p = None
            if isinstance(photo, InMemoryUploadedFile):
                upload_path_p = processUploadedImage(photo, 'events/poster/') 
                a.photo=upload_path_p
            icon = form.cleaned_data['icon']
            if icon == None:
                upload_path_i = None
            if isinstance(url, InMemoryUploadedFile):
                upload_path_i = processUploadedImage(icon, 'events/icon/')
                a.icon=upload_path_i 
            forum_url = form.cleaned_data['forum_url']
            gps_track = form.cleaned_data['gps_track']
            lat = form.cleaned_data['lat']
            lng = form.cleaned_data['lng']
            city = form.cleaned_data['city']
            description = form.cleaned_data['description']
            date = form.cleaned_data['date']
            user = request.user
            if lat == None:
                lat = 0 
            if lng == None:
                lng = 0 
            a.name=name
            a.text=text
            a.url=url
            a.reg_url=reg_url
            a.reg_status=reg_status
            a.forum_url=forum_url
            a.lat=lat
            a.lng=lng
            a.description=description
            a.date=date
            a.user = user
            a.save()

            for t in type: 
                a.type.add(t)
            a.save()
            return HttpResponseRedirect('/calendar/')
    else:
        form = EventsForm(instance=a)

    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'event_add.html', 'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'form': form}
    calendar = embeded_calendar()
    vars.update(calendar)        
    events = Events.objects.all().order_by('date')
    evnt = {'events': events}
    vars.update(evnt)
    return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))    
    