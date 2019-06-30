# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest
#from django.shortcuts import render_to_response
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpRequest, HttpResponseNotFound
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from django.shortcuts import render
import requests
import datetime, calendar, time
import hashlib
import smtplib
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from django.core.exceptions import ObjectDoesNotExist

from models import Events, RegEvent, ResultEvent, EventDistance
from forms import EventsForm, RegEventsForm, PayRegEventsForm

from portal.gallery.models import Album, Photo
from portal.funnies.views import get_funn
from portal.news.models import Route

from portal.accounting.models import ClientInvoice, Client, Catalog, Bicycle_Store, WorkType, WorkGroup, Discount, Type, Manufacturer, Bicycle_Type, YouTube

import simplejson
import googlemaps
import json

from portal.mysql_portal import get_month_event, get_month_events, get_day_events

from django.core.mail import send_mail
from datetime import date
#from django.core.context_processors import request
from django.utils.translation.trans_real import catalog

from django.db.models import Sum, Count, Max
from django.db.models import Q
from pyasn1.compat.octets import null

from django.views.decorators.csrf import csrf_exempt

#from gdata.contentforshopping.data import Manufacturer

def admin_sendmail(request, id):
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    calendar = embeded_calendar()
    if auth_group(request.user, 'admin')==False:
        vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'error_data': 'У вас не вистачає повноважень!'}
        return render(request, 'index.html', vars)
    revent = RegEvent.objects.get(pk = id)
    csum = revent.event.cur_reg_sum()
    if (type(csum) is tuple) and (csum[0] == "error"):
        vars = {'error_data': "Щось пішло не так. " + csum[1]}
        return render(request, 'index.html', vars)
        
    dleft = revent.event.days_left()

#    - на картку приватбанку (4323 3552 0025 8937 - Панчук Ігор) \n    
    message = """Нагадуємо що до заходу залишилось %s днів. \n 
    На даний момент реєстрація коштує %s гривень. Не затягуйте з оплатою адже чим ближче до заходу тим реєстраційний внесок більший.\n
    Оплату марафону можна здійснити: \n
    - оплатити в магазині Рівело (місто Рівне, вул.Кавказька 6) [http://www.rivelo.com.ua/about/] \n
    Внесіть будь-ласка дані про онлайн оплату за наступним посиланням http://rivelo.com.ua/event/rider/%s/pay/%s/ \n
    Інформацію по заходу можна знайти за посиланням  http://www.rivelo.com.ua/event/%s/show/ \n
    Список зареєстрованих знаходиться за цим посиланням http://www.rivelo.com.ua/event/%s/registration/list/ \n
    Гарних покатеньок і до зустрічі на старті.
    """ % (dleft, csum, id, revent.reg_code, revent.event.pk, revent.event.pk)
    
    #res = send_mail('Нагадування про оплату', message, revent.email, ['rivelo@ymail.com'], fail_silently=False)
    res = send_mail('Нагадування про оплату', message, revent.email, [revent.email], fail_silently=False)
        
    if res == 1:
        vars = {'success_data': "Лист відправлено на пошту " + revent.email, 'reglist': reverse('event-rider-list' , kwargs={'id':revent.event.pk})}
        #return render_to_response("index.html", {'success_data': "Лист відправлено на пошту " + revent.email}, context_instance=RequestContext(request, processors=[custom_proc]))
        return render(request, 'index.html', vars)
    #return render_to_response("index.html", {'success_data': "Щось пішло не так. Пошта " + revent.email}, context_instance=RequestContext(request, processors=[custom_proc]))
    vars = {'success_data': "Щось пішло не так. Пошта " + revent.email}
    return render(request, 'index.html', vars)


def html_content_right():
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    calendar = embeded_calendar()
    vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn()}
    return vars    


def admin_invite_mail(request, id, evnt=None):
    vars = html_content_right()
#    photo1 = Photo.objects.random()
#    photo2 = Photo.objects.random()
#    calendar = embeded_calendar()
    if auth_group(request.user, 'admin')==False:
        vars.update({'error_data': 'У вас не вистачає повноважень!'})
        return render(request, 'index.html', vars)
    revent = RegEvent.objects.get(pk = id)
    ev = None
    #vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn()}    
    try:
        ev = Events.objects.get(pk=evnt)
    except:
        vars.update({'success_data': "Щось пішло не так. Пошта " + revent.email})
        return render(request, 'index.html', vars)

#    csum = revent.event.cur_reg_sum()
    dleft = ev.days_left()

    
    message = """Запрошуємо Вас на нашу велоподію %s яка відбудеться %s \n
    %s \n
    Інформацію по заходу можна знайти за посиланням  %s \n
    Список зареєстрованих знаходиться за цим посиланням %s \n
    Нагадуємо що до заходу залишилось %s дні. Не забудьте зареєструватись завчасно. \n  
    Посилання на реєстрацію %s \n
    На даний момент реєстрація коштує %s гривень\n    
    Гарних покатеньок і до зустрічі на старті.
    """ % (ev.name, ev.date, ev.text, 'http://rivelo.com.ua/event/'+str(ev.pk)+'/show/', 'http://www.rivelo.com.ua/event/'+str(ev.pk)+'/registration/list/', dleft, 'http://www.rivelo.com.ua/event/'+str(ev.pk)+'/registration/', ev.cur_reg_sum())
    
    #res = send_mail('Нагадування про оплату', message, revent.email, ['rivelo@ymail.com'], fail_silently=False)
    res = send_mail('запрошуємо на велоподію "'+ ev.name +'"', message, revent.email, [revent.email], fail_silently=False)
            
    if res == 1:
        #return render_to_response("index.html", {'success_data': "Лист відправлено на пошту " + revent.email}, context_instance=RequestContext(request, processors=[custom_proc]))
        vars.update({'success_data': "Лист відправлено на пошту " + revent.email, 'reglist': 'http://www.rivelo.com.ua/event/'+str(ev.pk)+'/registration/list/'})
        return render(request, "index.html", vars)
    vars.update({'success_data': "Щось пішло не так. Пошта " + revent.email, 'reglist': 'http://www.rivelo.com.ua/event/'+str(ev.pk)+'/registration/list/'})
    return render(request, "index.html", vars)

#===============================================================================
#    from_mail = settings.EMAIL_HOST_USER #settings.DEFAULT_FROM_EMAIL  
#    email_text = """\
#    From: %s  
#    To: %s  
#    Subject: %s
#    %s
#    """ % (from_mail, ", ".join(to), subject, message)
#    try:  
#        server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
#        server.ehlo()
#        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
#        server.sendmail(from_mail, to, email_text)
#        server.close()
#        return ('ok', 'Лист успішно відправлено')
#    except:  
#        return ('error', 'Щось пішло не так')
#===============================================================================


def send_reg_mail(request, rid, mto, subject='Реєстрація'):
    revent = RegEvent.objects.get(pk = rid)
    everules = revent.event.rules.all()
    w = None
    if request.session.get("registration_subject"):
#        w = render_to_response('event_rider_info.html', {'rider': revent, 'thismail' : True, 'default_domain': settings.DEFAULT_DOMAIN, 'main_text': 'Ви успішно відредагували свої дані на марафон ', 'event_rules': everules})
        w = render(request, 'event_rider_info.html', {'rider': revent, 'thismail' : True, 'default_domain': settings.DEFAULT_DOMAIN, 'main_text': 'Ви успішно відредагували свої дані на марафон ', 'event_rules': everules}, content_type='application/xhtml+xml')
    else:
#        w = render_to_response('event_rider_info.html', {'rider': revent, 'thismail' : True, 'default_domain': settings.DEFAULT_DOMAIN, 'main_text': 'Вітаємо ви успішно зареєструвались на марафон ', 'event_rules': everules })
        w = render(request, 'event_rider_info.html', {'rider': revent, 'thismail' : True, 'default_domain': settings.DEFAULT_DOMAIN, 'main_text': 'Вітаємо ви успішно зареєструвались на марафон ', 'event_rules': everules }, content_type='application/xhtml+xml')
    from_email = 'rivno100@gmail.com' 
    to = mto
    text_content = 'www.rivelo.com.ua'
    html_content = w.content
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return render(request, "index.html", {'success_data': "Лист відправлено на пошту" + to})


def email_two(rid, mto):
    subject = "Реєстрація. Дані про оплату"
    to = [mto]
    from_email = 'rivno100@gmail.com'
    revent = RegEvent.objects.get(pk = rid)
    ctx = {
        'rider': revent, 
#        'thismail' : True,
        'add_pay': True,
        'default_domain': settings.DEFAULT_DOMAIN,
    }

    message = get_template('event_rider_info.html').render(Context(ctx))
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()
    return 'Лист успішно відправлено'


def custom_proc(request):
# "A context processor that provides 'app', 'user' and 'ip_address'."
    return {
        'app': 'Rivelo portal',
        'user': request.user,
        'ip_address': request.META['REMOTE_ADDR']
    }


def auth_group(user, group):
    return True if user.groups.filter(name=group) else False


def processUploadedImage(file, dir=''): 
    upload_suffix = 'upload/' + dir + file.name
    upload_path = settings.MEDIA_ROOT + 'upload/' + file.name
        
    destination = open(settings.MEDIA_ROOT + 'upload/'+ dir + file.name, 'wb+')
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

#    return {'weeks': month_calendar, 'events': get_month_event(year, month),
    return {'weeks': month_calendar, 'sel_day': today, 'sel_date': selected_date, 
            'prev_month': prev_date, 'next_month': next_date, 'year': year, 'events_date': list} 
#            'prev_month': prev_date, 'next_month': next_date, 'month_events': month_events , 'year': year, 'events_date': list}
    
    
#===============================================================================
# def calendar_page(request, year=datetime.datetime.now().year):
#     photo1 = Photo.objects.random()
#     photo2 = Photo.objects.random()
#     calendar = embeded_calendar()
#     vars = {'weblink': 'event_list.html', 'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn()}
#     calendar = embeded_calendar()
#     vars.update(calendar)    
#     events = Events.objects.filter(date__year = year).order_by('date') #.all().order_by('date')
#     evnt = {'events': events}
#     vars.update(evnt)
#     return render(request, 'index.html', vars)
#     #return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))
#===============================================================================

#def calendar_filter(request, year=datetime.datetime.now().year, month=None):
def calendar_page(request, year=datetime.datetime.now().year, month=None):
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    calendar = embeded_calendar()
    vars = {'weblink': 'event_list.html', 'sel_menu': 'calendar', 'month': month, 'photo1': photo1, 'photo2': photo2, 'entry': get_funn()}
    calendar = embeded_calendar()
    calendar['year'] = year
    vars.update(calendar)    
    if month == None:
        events = Events.objects.filter(date__year = year).order_by('date')
    else:
        events = Events.objects.filter(date__year = year, date__month = month).order_by('date')
    evnt = {'events': events}
    vars.update(evnt)
    return render(request, 'index.html', vars)
    #return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))


def google_location(request):
    gmaps = googlemaps.Client(key='AIzaSyDR8YRTxz9xNV1F75RQp1IwKA4Dt6MBUKQ')
    res = gmaps.places_autocomplete("Рівн", language="uk", type='(regions)', components={'country': 'ua'})
    str = "<br>"
    for i in res:
        str = str + i['terms'][0]['value']+ " / " + i['description'] + "<br>"  
#    return HttpResponse("Список міст:" + res[0]['terms'][0]['value'])
    return HttpResponse("<b>Список міст:</b>" + str)

@csrf_exempt
def get_event(request):
    if auth_group(request.user, 'moder')==False:
    #if request.user.is_authenticated()==False:
        return HttpResponse("<h2>Для виконання операції, авторизуйтесь</h2>")

#    date_before = datetime.datetime.today() - datetime.timedelta(days=180)
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('dates'):
                d = request.POST['dates']
                date_y = int(d[6:])
                date_m = int(d[3:5])
                date_d = int(d[:2])
                elist = Events.objects.filter(date__year = date_y, date__month = date_m, date__day = date_d).values("name", "text", "type", "icon", "date", "photo", "user__username", "pub_date", "forum_url", "reg_url", "pk", "reg_status")
                json = list(elist)
                for x in json:  
                    x['date'] = x['date'].strftime("%d/%m/%Y")
                    x['pub_date'] = x['pub_date'].strftime("%d/%m/%Y")
                #json = serializers.serialize('json', p_cred_month, fields=('id', 'date', 'price', 'description', 'user', 'user_username'))
                return HttpResponse(simplejson.dumps(json), content_type='application/json')
    
    return HttpResponse(elist, content_type='application/json')        


#from django.contrib.auth.models import User

def add_event(request):
#    print "Form WORK"
    if auth_group(request.user, 'moder')==False:
    #if request.user.is_authenticated()==False:
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
            time_e = form.cleaned_data['time']
            date.replace(hour=time_e.hour, minute=time_e.minute)
            date = datetime.datetime.combine(date, time_e)
            cup = form.cleaned_data['cup']
            user = request.user
            if lat == None:
                lat = 0 
            if lng == None:
                lng = 0 
            evt = Events(name=name, text=text, url=url, reg_url=reg_url, reg_status=reg_status, photo=photo, icon=icon, forum_url=forum_url, lat=lat, lng=lng, description=description, date=date, city=city, user = user, cup=cup)
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
    return render(request, 'index.html', vars)
    #return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))    
  


def edit_event(request, id):
    if auth_group(request.user, 'moder')==False:
    #if request.user.is_authenticated()==False:
        return HttpResponse("<h2>Для виконання операції, авторизуйтесь</h2>")
    a = Events.objects.get(pk=id)
    if request.method == 'POST':
        form = EventsForm(request.POST, request.FILES, instance=a)
        if form.is_valid():
            name = form.cleaned_data['name']
            type = form.cleaned_data['type']
            text = form.cleaned_data['text']
            url = form.cleaned_data['url']
            reg_url = form.cleaned_data['reg_url']
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
            time_e = form.cleaned_data['time']
            date.replace(hour=time_e.hour, minute=time_e.minute)
            date = datetime.datetime.combine(date, time_e)
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
            a.description = description
            a.date = date
            a.city = city
            a.user = user
            a.save()

#            if reg_status == True:
#                reg_url = "/event/"+ str(a.pk) +"/registration/"
#            a.reg_url = reg_url

            for t in type: 
                a.type.add(t)
            a.save()
            return HttpResponseRedirect('/calendar/')
    else:
        stime = a.date.strftime("%H:%M")
        form = EventsForm(instance=a, initial={'time': stime})

    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'event_add.html', 'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'form': form}
    calendar = embeded_calendar()
    vars.update(calendar)        
    events = Events.objects.all().order_by('date')
    evnt = {'events': events}
    vars.update(evnt)
    return render(request, 'index.html', vars)
    #return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))    


def show_event(request, id):
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'event_show.html', 'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn()}
    calendar = embeded_calendar()
    vars.update(calendar)        
    event = Events.objects.get(pk = id)
    evnt = {'event': event}
    vars.update(evnt)
    return render(request, 'index.html', vars)
    #return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))    
    
    
@csrf_exempt
def get_event_gps(request):
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('eid'):
                eid = request.POST['eid']
                elist = Events.objects.filter(pk = eid).values("name", "user__username", "gps_track")
                json = list(elist)
                return HttpResponse(simplejson.dumps(json), content_type='application/json')
    
    return HttpResponse(elist, content_type='application/json')        

    
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def grecaptcha_verify(request):
    if request.method == 'POST':
        response = {}
        data = request.POST
        captcha_rs = data.get('g-recaptcha-response')
        url = "https://www.google.com/recaptcha/api/siteverify"
        params = {
            'secret': settings.RECAPTCHA_SECRET_KEY,
#            'secret': "6LeptAUTAAAAAMWpC4bEiwcDvda48vC8IcCzQJNf",
            'response': captcha_rs,
            'remoteip': get_client_ip(request)
        }
        verify_rs = requests.get(url, params=params, verify=True)
        verify_rs = verify_rs.json()
        response["status"] = verify_rs.get("success", False)
        response['message'] = verify_rs.get('error-codes', None) or "Unspecified error."
        #return HttpResponse(response, content_type="text/plain")
        return response
  
    
def add_reg(request, id):
    a = Events.objects.get(pk=id)
    r = RegEvent(event = a)
    dl = a.days_left()

    vars = None
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    calendar = embeded_calendar()
    
    if (a.days_left() <= 0):
        if (auth_group(request.user, 'admin')==False):
            vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'error_data': "Реєстрацію завершено, або ви не авторизувались для даної функції. До старту заходу " + str(a.days_left()) + " днів"}
            vars.update(calendar)        
            evnt = {'event': a}
            vars.update(evnt)
            return render(request, 'index.html', vars)
#            return HttpResponse("Реєстрацію завершено, або ви не авторизувались для даної функції. До старту заходу " + str(a.days_left()) + " днів", content_type="text/plain")
#    r = RegEvent()
    
    
    if request.method == 'POST':
        #form = RegEventsForm(request.POST, dist, instance=r, event_id = a.pk)
        form = RegEventsForm(request.POST, instance=r, event_id = a.pk)
        gr = grecaptcha_verify(request)
        if gr['status'] == False:
            vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'error_data': 'Пройдіть підтвердження що ви не робот'}
            vars.update(calendar)        
            evnt = {'event': a}
            vars.update(evnt)
            return render(request, 'index.html', vars)
            
            # https://developers.google.com/recaptcha/docs/verify
        if form.is_valid():
            event = form.cleaned_data['event']
            fname = form.cleaned_data['fname']
            lname = form.cleaned_data['lname']
            nickname = form.cleaned_data['nickname']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            country = form.cleaned_data['country']
            city = form.cleaned_data['city']
            club = form.cleaned_data['club']
            bike_type = form.cleaned_data['bike_type']
            birthday = form.cleaned_data['birthday']
            #pay = form.cleaned_data['pay']
            #date = form.cleaned_data['date']
            sex = form.cleaned_data['sex']
            description = form.cleaned_data['description']
            distance_type = form.cleaned_data['distance_type']
#            event = a
            
            regevt = RegEvent(event=Events.objects.get(pk=id), fname=fname, lname=lname, nickname=nickname, email=email, phone=phone, country=country, city=city, club=club, bike_type=bike_type, birthday=birthday, sex=sex, distance_type=distance_type, description = description)
#            regevt = RegEvent(event=event, fname=fname, lname=lname, nickname=nickname, email=email, phone=phone, country=country, city=city, club=club, bike_type=bike_type, birthday=birthday, sex=sex, distance_type=distance_type, description = description)            
            regevt.save()
            reg_code = hashlib.sha256(str(regevt.pk)).hexdigest()
            regevt.reg_code = reg_code 
            regevt.save()
            
            request.session['registrationcode'] = reg_code
            request.session.set_expiry(0)
            request.session.set_test_cookie()
            #request.session.clear()
            if request.session.test_cookie_worked() == False:
                vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'error_data': 'У вас вимкнено Cookie, для повноцінної роботи увімкніть їх'}
                vars.update(calendar)        
                evnt = {'event': a}
                vars.update(evnt)
                return render(request, 'index.html', vars)                
                #return HttpResponse("Cookie don't work!!!" +  request.session['registrationcode'], content_type="text/plain")
            request.session.delete_test_cookie()
            try:
                del request.session['reg_email']
                del request.session["registration_subject"]
            except:
                error = "відсутній параметр reg_email"
            return HttpResponseRedirect('/event/rider/'+str(regevt.pk)+'/info/')
    else:
        form = RegEventsForm(instance=r, event_id = a.pk)
        #form = RegEventsForm(instance=r)
        
    vars = {'weblink': 'event_reg_add.html', 'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'form': form}
    vars.update(calendar)        
    evnt = {'event': a}
    vars.update(evnt)
    return render(request, 'index.html', vars)
    #return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))        


def edit_reg(request, id, hash):
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    calendar = embeded_calendar()

    revent = RegEvent.objects.get(pk = id)
    a = revent.event
    if hash != revent.reg_code:
        vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'error_data': 'Ваше посилання вже не є актуальним! '}
        return render(request, 'index.html', vars)

    if request.method == 'POST':
        form = RegEventsForm(request.POST, instance=revent, event_id = a.id, edit=True)
        gr = grecaptcha_verify(request)
        if gr['status'] == False:
            vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'error_data': 'Пройдіть підтвердження що ви не робот'}
            vars.update(calendar)        
            evnt = {'event': a}
            vars.update(evnt)
            return render(request, 'index.html', vars)
            
            # https://developers.google.com/recaptcha/docs/verify
        if form.is_valid():
            form.save()
            revent.event = a
            revent.save()
#            reg_code = hashlib.sha256(str(revent.pk)).hexdigest()
#            regevt.reg_code = reg_code 
#            regevt.save()
            request.session['registrationcode'] = revent.reg_code
            request.session.set_expiry(0)
            request.session.set_test_cookie()
            #request.session.clear()
            if request.session.test_cookie_worked() == False:
                vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'error_data': 'У вас вимкнено Cookie, для повноцінної роботи увімкніть їх'}
                vars.update(calendar)        
                evnt = {'event': a}
                vars.update(evnt)
                return render(request, 'index.html', vars)                
                #return HttpResponse("Cookie don't work!!!" +  request.session['registrationcode'], content_type="text/plain")
            request.session.delete_test_cookie()
            try:
                del request.session['reg_email']
            except:
                error = "Параметр reg_email не існує"
            request.session["registration_subject"] = 'Реєстрація. Редагування даних'            
            return HttpResponseRedirect('/event/rider/'+str(revent.pk)+'/info/')
    else:
        form = RegEventsForm(instance=revent, event_id = a.id, edit=True)
        
    vars = {'weblink': 'event_reg_add.html', 'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'form': form}
    vars.update(calendar)        
    evnt = {'event': a}
    vars.update(evnt)
    return render(request, 'index.html', vars)
    #return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))        


def event_reg_list(request, id, start=False):
    evt = Events.objects.get(pk=id)
    revent = None
    if start == True:
        revent = RegEvent.objects.filter(event = id, start_status = True).order_by("date") #all rider list
    else:
        revent = RegEvent.objects.filter(event = id).order_by("date") #all rider list
    event_date = evt.date
    #curyear = datetime.datetime.now().year
    cat0_b = event_date.replace(year = event_date.year-12)
    cat0_e = event_date.replace(year = event_date.year-18)
    if start == True:
        revent_cat0 = RegEvent.objects.filter(event = id, birthday__lte = cat0_b.date(), birthday__gte = cat0_e.date(), start_status = True).order_by("date") #all rider list
    else:
        revent_cat0 = RegEvent.objects.filter(event = id, birthday__lte = cat0_b.date(), birthday__gte = cat0_e.date()).order_by("date") #all rider list
    cat1_b = event_date.replace(year = event_date.year-18)
    cat1_e = event_date.replace(year = event_date.year-30)
    #revent_cat1 = RegEvent.objects.filter(event = id, birthday__lte = datetime.date(1999, 1, 5), birthday__gte = datetime.date(1987, 1, 5)).order_by("date") #all rider list
    if start == True:
        revent_cat1 = RegEvent.objects.filter(event = id, birthday__lte = cat1_b.date(), birthday__gte = cat1_e.date(), start_status = True).order_by("date") #all rider list
    else:
        revent_cat1 = RegEvent.objects.filter(event = id, birthday__lte = cat1_b.date(), birthday__gte = cat1_e.date()).order_by("date") #all rider list
    #RegEvent.objects.filter(event = id, birthday__range=[cat1_e, cat1_b])
    cat2_b = event_date.replace(year = event_date.year-30)
    cat2_e = event_date.replace(year = event_date.year-40)
    if start == True:    
        revent_cat2 = RegEvent.objects.filter(event = id, birthday__lte = cat2_b.date(), birthday__gte = cat2_e.date(), start_status = True).order_by("date") #all rider list
    else:
        revent_cat2 = RegEvent.objects.filter(event = id, birthday__lte = cat2_b.date(), birthday__gte = cat2_e.date()).order_by("date") #all rider list
    cat3_b = event_date.replace(year = event_date.year-40)
    cat3_e = event_date.replace(year = event_date.year-50)
    if start == True: 
        revent_cat3 = RegEvent.objects.filter(event = id, birthday__lte = cat3_b.date(), birthday__gte = cat3_e.date(), start_status = True).order_by("date") #all rider list
    else:
        revent_cat3 = RegEvent.objects.filter(event = id, birthday__lte = cat3_b.date(), birthday__gte = cat3_e.date()).order_by("date") #all rider list
    cat4_b = event_date.replace(year = event_date.year-50)
    cat4_e = event_date.replace(year = event_date.year-60)
    if start == True: 
        revent_cat4 = RegEvent.objects.filter(event = id, birthday__lte = cat4_b.date(), birthday__gte = cat4_e.date(), start_status = True).order_by("date") #all rider list
    else:
        revent_cat4 = RegEvent.objects.filter(event = id, birthday__lte = cat4_b.date(), birthday__gte = cat4_e.date()).order_by("date") #all rider list
    cat5_b = event_date.replace(year = event_date.year-60)
    if start == True:
        revent_cat5 = RegEvent.objects.filter(event = id, birthday__lte = cat5_b.date(), start_status = True).order_by("date") #all rider list
    else:
        revent_cat5 = RegEvent.objects.filter(event = id, birthday__lte = cat5_b.date()).order_by("date") #all rider list
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    evnt_reg = Events.objects.filter(reg_status = True)
    vars = {'weblink': 'event_reg_list.html', 'sel_menu': 'calendar', 'start': start, 'evnt_reg': evnt_reg, 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'list': revent, 'cat0': revent_cat0, 'cat1': revent_cat1, 'cat2': revent_cat2, 'cat3': revent_cat3, 'cat4': revent_cat4, 'cat5': revent_cat5}
    calendar = embeded_calendar()
    vars.update(calendar)        

    evnt = {'event': evt}
    vars.update(evnt)
    try:
        del request.session['reg_email']
    except:
        error = "Параметр reg_email не існує"
    return render(request, 'index.html', vars)        
    #return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))        
    

@csrf_exempt    
def event_reg_edit(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponse("У вас не достатньо повноважень для даної функції", content_type="text/plain")
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('rid'):
                rid = request.POST['rid']
                number = request.POST['number']
                rider = RegEvent.objects.get(pk = rid)
                chk_event = rider.event
                #res = RegEvent.objects.filter(event = chk_event, start_number = number).values_list('start_number', flat=True).order_by('start_number')
                res = RegEvent.objects.filter(event = chk_event, start_number__gt=0).exclude(id = rid).values_list('start_number', flat=True).order_by('start_number')
                if len(res) > 0 :
                    nlist = ', '.join(map(str, res))
                    #return HttpResponse("Номер %s вже вибраний. Виберіть інший окрім (%s)" % (number, nlist))
                    if int(number) in res:
                        return HttpResponse("Номер %s вже вибраний. Виберіть інший окрім (%s)" % (number, nlist))
                rider.start_number = number
                rider.save()
                return HttpResponse(rider.start_number, content_type='text/plain')
    
    return HttpResponse("Щось пішло не так :(", content_type='text/plain')        
    
   
def get_event_rider(request, id):
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
        return HttpResponse("У вашому браузері не працюють куки/Cookie. ")

    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    
    revent = RegEvent.objects.get(pk = id)
    code = request.session.get("registrationcode")
#    print "CODE#1 = ", revent.pk
    if not code and auth_group(request.user, 'admin')==False:
#    if "registrationcode" in request.session :
        vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'error_data': 'Ваше посилання вже не є актуальним!'}
        return render(request, 'index.html', vars)
#        return HttpResponse("Ваше посилання вже не є актуальним! model = " + revent.reg_code, content_type="text/plain")

    if request.session.get('registrationcode') != revent.reg_code and auth_group(request.user, 'admin')==False:
        vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'error_data': 'Ваше посилання вже не є актуальним!'}
        return render(request, 'index.html', vars)
    #if request.session['registrationcode'] != revent.reg_code :
#        return HttpResponse("Ваше посилання вже не є актуальним!!! model = " + revent.reg_code + "  SESSION_ID = "+ str(request.session.get('registrationcode'))+ "AUTH = " + str(auth_group(request.user, 'admin')), content_type="text/plain")
     
                            #request.COOKIES['sessionid'], content_type="text/plain")
    everules = revent.event.rules.all()
    vars = {'weblink': 'event_rider_info.html', 'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'rider': revent, 'reg_ok': True, 'event_rules': everules}
    calendar = embeded_calendar()
    vars.update(calendar)        
    
    regmail = request.session.get("reg_email")
    if (not regmail) and (regmail != True):
        if request.session.get("registration_subject"):
            #request.session.get["registration_subject"]
            send_reg_mail(request, revent.pk, revent.email, "Редагування даних")
            print "Email reg_subj = ", revent.email
        else:
            print "Email = ", revent.email
            send_reg_mail(request, revent.pk, revent.email)
        res_data = "EMail надіслано"
        request.session['reg_email'] = True
    #return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))
    return render(request, 'index.html', vars)        

# внесення даних про оплату
def add_rider_pay(request, id, hash=None):
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    revent = RegEvent.objects.get(pk = id)    
    if hash != None and hash != revent.reg_code:
        vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'error_data': 'Ваше посилання вже не є актуальним!'}
        return render(request, 'index.html', vars)
    
    if hash == None and auth_group(request.user, 'admin')==False:
        vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'error_data': 'Ваше посилання вже не є актуальним або у вас не вистачає повноважень!'}
        return render(request, 'index.html', vars)
        
#    else:
#        vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'success_data': res_data}
#        return render(request, 'index.html', vars)
    if request.method == 'POST':
        form = PayRegEventsForm(request.POST, instance=revent, request=request)
        if form.is_valid():
            pay = form.cleaned_data['pay']
            #pay_date = form.cleaned_data['pay_date']
            pay_type = form.cleaned_data['pay_type']
            start_number = form.cleaned_data['start_number']
            description = form.cleaned_data['description']
            date = form.cleaned_data['pay_date']
            time_e = form.cleaned_data['pay_time']
            #date.replace(hour=time_e.hour, minute=time_e.minute)
            pay_date = datetime.datetime.combine(date, time_e)

            revent.pay=pay
            revent.pay_type=pay_type
            revent.pay_date=pay_date
            revent.start_number=start_number
            revent.description=description
            reg_code = hashlib.sha256(str(revent.pk)+str(revent.pay)).hexdigest()
            revent.reg_code = reg_code 
            revent.save()
            #if (not paymail) and (paymail != True):
            try:
                email_two(revent.pk, revent.email)
            except:
                vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'error_data': 'Сталася помилка. Звяжіться з адміністратором rivno100@gmail.com'}
                return render(request, 'index.html', vars)
                
            vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'success_data': 'Дякуємо за внесені дані, після перевірки адміністрацією Вас буде відмічено на протязі доби', 'reglist': '/event/'+str(revent.event.pk)+'/registration/list/'}
            return render(request, 'index.html', vars)
            
#            return HttpResponseRedirect(reverse('event-rider-list', args=[revent.event.pk])) 
    else:
        form = PayRegEventsForm(instance=revent)

    vars = {'weblink': 'event_reg_add.html', 'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'form': form, 'google_city_off': True}
    calendar = embeded_calendar()
    vars.update(calendar)        
    evname = {'event': revent.event}
    vars.update(evname)
    rname = "%s %s [%s]" % (revent.fname, revent.lname, revent.nickname)
    rider_n = {'rider_name': rname}
    vars.update(rider_n)
    evrules = revent.event.rules.all()
    rules = {'event_rules': evrules}
    vars.update(rules)
    
    return render(request, 'index.html', vars)    


def register_to_all(request, hash):
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    try:
        revent = RegEvent.objects.get(reg_code = hash)
        event_list = Events.objects.filter(reg_status=True)
    except RegEvent.DoesNotExist:
        revent = None
        vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'error_data': 'Ваше посилання вже не є актуальним! У разі питань зверніться до адміністрації за адресою rivno100@gmail.com'}
        return render(request, 'index.html', vars)
    except RegEvent.MultipleObjectsReturned:
        revent = RegEvent.objects.filter(reg_code = hash)
        vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'reg_data':revent, 'error_data': 'Вас зареєстровано декілька разів! У разі питань зверніться до адміністрації за адресою rivno100@gmail.com'}
        return render(request, 'index.html', vars)

    if hash != revent.reg_code:
        vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'error_data': 'Ваше посилання вже не є актуальним! У разі питань зверніться до адміністрації за адресою rivno100@gmail.com'}
        return render(request, 'index.html', vars)

    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'event_rider_info.html', 'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'rider': revent, 'register_all': True, 'reg_event_list': event_list, 'default_domain': settings.DEFAULT_DOMAIN}
    calendar = embeded_calendar()
    vars.update(calendar)        
    regmail = request.session.get("reg_email")
    if (not regmail) and (regmail != True):
        send_reg_mail(request, revent.pk, revent.email)
        res_data = "EMail надіслано"
        request.session['reg_email'] = True
    return render(request, 'index.html', vars)
    #return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))        


def send_reg_qr_code(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponse("У вас не достатньо повноважень для даної функції", content_type="text/plain")
    event_id = id
    riders = RegEvent.objects.filter(event__pk = event_id, status = True)
    #riders = RegEvent.objects.filter(event__pk = event_id, nickname='ygrik')
    for rid in riders:
        qrcode_str = '<a href="'+settings.DEFAULT_DOMAIN+'/rider/'+str(rid.id)+'/regstatus/">Посилання на код</a>'                                            
        email_text = """Ви отримали лист в якому знаходиться QR-код для швидкого отримання стартового пакету.<br> Ви можете його зберегти, або в будь-який час отримати онлайн, для предявлення на старті. """ + qrcode_str  
        email_text = email_text + '<br><img src="http://chart.apis.google.com/chart?chs=500x500&cht=qr&chl='+str(rid.id)+'&choe=UTF-8&chld=H|0"/>'
        message = email_text    
        res = send_mail('Марафон 100 миль 2019 року. QR-code.', message, rid.email, [rid.email], fail_silently=False, html_message=email_text)
#        if res:
#            print "Mail was send to email " + rid.email
    return HttpResponse("Листи відправлено на пошту ", content_type='text/plain;charset=utf-8')
    #return HttpResponse("Щось пішло не так :(", content_type='text/plain')            


@csrf_exempt
def event_rider_status(request):
    if auth_group(request.user, 'admin')==False:
        return HttpResponse("У вас не достатньо повноважень для даної функції", content_type="text/plain")
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('rid'):
                rid = request.POST['rid']
                rider = RegEvent.objects.get(pk = rid)
                rider.status = not rider.status
                rider.save()
                if rider.status == True:
                    #qrcode_str = '<img src="http://chart.apis.google.com/chart?chs=500x500&cht=qr&chl='+str(rid)+'&choe=UTF-8&chld=H|0"/>'
                    qrcode_str = '<a href="'+settings.DEFAULT_DOMAIN+'/rider/'+str(rid)+'/regstatus/">Посилання на код</a>'                                            
                    email_text = """Ви отримали лист в якому знаходиться QR-код для швидкого отримання стартового пакету.<br> Ви можете його зберегти, або в будь-який час отримати онлайн, для предявлення на старті. """ + qrcode_str  
                    email_text = email_text + '<br><img src="http://chart.apis.google.com/chart?chs=500x500&cht=qr&chl='+str(rid)+'&choe=UTF-8&chld=H|0"/>'
                    message = email_text    
                    res = send_mail('Марафон 100 миль 2019 року. QR-code.', message, rider.email, [rider.email], fail_silently=False, html_message=email_text)

                json = dict(status = rider.status)
                return HttpResponse(simplejson.dumps(json), content_type='application/json')
    
    return HttpResponse("Щось пішло не так :(", content_type='text/plain')        


@csrf_exempt
def rider_start_status(request):
    if auth_group(request.user, 'admin')==False:
        if request.body:
            POST = json.loads(request.body)
            if (('rid' in POST) and ('chkhash' in POST)):
                chkhash = POST['chkhash']
                rid = POST['rid']
                if chkhash <> settings.CHK_APP_HASH: #'Rivelo256haSh+1234567890-2019':
                    return HttpResponseBadRequest('hash not found or invalid')
                try:
                    rev = RegEvent.objects.get(pk = rid)
                    rev.start_status = True
                    rev.save()
                    json_data = dict(status = True)
                    return HttpResponse(simplejson.dumps(json_data), content_type='application/json')
                except RegEvent.DoesNotExist:
                    return HttpResponse("Id "+ rid +" is not found", content_type='text/plain')
        return HttpResponse("У вас не достатньо повноважень для даної функції", content_type="text/plain")
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('rid'):
                rid = request.POST['rid']
                rider = RegEvent.objects.get(pk = rid)
                rider.start_status = not rider.start_status
                rider.save()
                json_data = dict(status = rider.start_status)
                return HttpResponse(simplejson.dumps(json_data), content_type='application/json')
    
    return HttpResponse("Щось пішло не так :(", content_type='text/plain')        


def event_result(request, id):
    evt = Events.objects.get(pk=id)
    kp2 = False
    kp3 = False
#    revent = ResultEvent.objects.filter(reg_event__event = id, reg_event__start_status = True).order_by("-finish") #.values("fname", "lname", "sex", "nickname", "start_number", "status",  "resultevent__kp1", "resultevent__finish", "resultevent__start",  "pk", 'id', 'email', 'phone', 'city', 'birthday', 'club', 'bike_type', 'pay', 'description').order_by("date") #all rider list
    revent = ResultEvent.objects.filter(reg_event__event = id).order_by("-finish") #.values("fname", "lname", "sex", "nickname", "start_number", "status",  "resultevent__kp1", "resultevent__finish", "resultevent__start",  "pk", 'id', 'email', 'phone', 'city', 'birthday', 'club', 'bike_type', 'pay', 'description').order_by("date") #all rider list
    if revent.exclude(kp2 = None):
        kp2 = True
    if revent.exclude(kp3 = None):
        kp3 = True
    #revent = RegEvent.objects.filter(event = id, start_status = True).values("fname", "lname", "sex", "nickname", "start_number", "status",  "resultevent__kp1", "resultevent__finish", "resultevent__start",  "pk", 'id', 'email', 'phone', 'city', 'birthday', 'club', 'bike_type', 'pay', 'description').order_by("date") #all rider list    
    event_date = evt.date
    #curyear = datetime.datetime.now().year
    cat0_b = event_date.replace(year = event_date.year-12)
    cat0_e = event_date.replace(year = event_date.year-18)
    #revent_cat0 = ResultEvent.objects.filter(reg_event__event = id, reg_event__birthday__lte = cat0_b, reg_event__birthday__gte = cat0_e.date, reg_event__start_status = True).order_by("-finish") #all rider list
    revent_cat0 = ResultEvent.objects.filter(reg_event__event = id, reg_event__birthday__lte = cat0_b.date(), reg_event__birthday__gte = cat0_e.date(), reg_event__start_status = True).order_by("-finish") #all rider list    
    cat1_b = event_date.replace(year = event_date.year-18)
    cat1_e = event_date.replace(year = event_date.year-30)
    #revent_cat1 = ResultEvent.objects.filter(reg_event__event = id, reg_event__birthday__lte = cat1_b, reg_event__birthday__gte = cat1_e.date, reg_event__start_status = True).order_by("-finish") #all rider list
    revent_cat1 = ResultEvent.objects.filter(reg_event__event = id, reg_event__birthday__lte = cat1_b.date(), reg_event__birthday__gte = cat1_e.date(), reg_event__start_status = True).order_by("-finish") #all rider list
    cat2_b = event_date.replace(year = event_date.year-30)
    cat2_e = event_date.replace(year = event_date.year-40)
    #revent_cat2 = ResultEvent.objects.filter(reg_event__event = id, reg_event__birthday__lte = cat2_b, reg_event__birthday__gte = cat2_e, reg_event__start_status = True).order_by("-finish") #all rider list
    revent_cat2 = ResultEvent.objects.filter(reg_event__event = id, reg_event__birthday__lte = cat2_b.date(), reg_event__birthday__gte = cat2_e.date(), reg_event__start_status = True).order_by("-finish") #all rider list
    cat3_b = event_date.replace(year = event_date.year-40)
    cat3_e = event_date.replace(year = event_date.year-50)
    #revent_cat3 = ResultEvent.objects.filter(reg_event__event = id, reg_event__birthday__lte = cat3_b, reg_event__birthday__gte = cat3_e, reg_event__start_status = True).order_by("-finish") #all rider list
    revent_cat3 = ResultEvent.objects.filter(reg_event__event = id, reg_event__birthday__lte = cat3_b.date(), reg_event__birthday__gte = cat3_e.date(), reg_event__start_status = True).order_by("-finish") #all rider list
    cat4_b = event_date.replace(year = event_date.year-50)
    cat4_e = event_date.replace(year = event_date.year-60)
    revent_cat4 = ResultEvent.objects.filter(reg_event__event = id, reg_event__birthday__lte = cat4_b.date(), reg_event__birthday__gte = cat4_e.date(), reg_event__start_status = True).order_by("-finish") #all rider list
    #revent_cat4 = ResultEvent.objects.filter(reg_event__event = id, reg_event__birthday__lte = cat4_b, reg_event__birthday__gte = cat4_e, reg_event__start_status = True).order_by("-finish") #all rider list
    cat5_b = event_date.replace(year = event_date.year-60)
    #revent_cat5 = ResultEvent.objects.filter(reg_event__event = id, reg_event__birthday__lte = cat5_b, reg_event__start_status = True).order_by("-finish") #all rider list
    revent_cat5 = ResultEvent.objects.filter(reg_event__event = id, reg_event__birthday__lte = cat5_b.date(), reg_event__start_status = True).order_by("-finish") #all rider list
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
#    vars = {'weblink': 'event_rider_result.html', 'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'list': revent, 'cat0': revent_cat0, 'cat1': revent_cat1, 'cat2': revent_cat2, 'cat3': revent_cat3, 'cat4': revent_cat4, 'cat5': revent_cat5}
    vars = {'weblink': 'event_rider_result.html', 'sel_menu': 'calendar', 'list': revent, 'entry': get_funn(), 'gcity': ResultEvent.group_city.filter(reg_event__event = id), 'cat0': revent_cat0, 'cat1': revent_cat1, 'cat2': revent_cat2, 'cat3': revent_cat3, 'cat4': revent_cat4, 'cat5': revent_cat5, 'kp2': kp2, 'kp3': kp3}    
#    calendar = embeded_calendar()
#    vars.update(calendar)        
    evnt = {'event': evt}
    vars.update(evnt)
    try:
        del request.session['reg_email']
    except:
        error = "Параметр reg_email не існує"
    #return render(request, 'index_result.html', vars)
#    return render(request, 'index.html', vars)
    try:
        return render(request, 'index.html', vars)
    except:
        return HttpResponse("Результатів ще не має", content_type='text/plain;charset=utf-8')
    #return render_to_response('index_result.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))        


def event_result_uat(request, id):
    evt = Events.objects.get(pk=id)
    kp2 = False
    kp3 = False
#    revent = ResultEvent.objects.filter(reg_event__event = id, reg_event__start_status = True).order_by("-finish") #.values("fname", "lname", "sex", "nickname", "start_number", "status",  "resultevent__kp1", "resultevent__finish", "resultevent__start",  "pk", 'id', 'email', 'phone', 'city', 'birthday', 'club', 'bike_type', 'pay', 'description').order_by("date") #all rider list
    revent = ResultEvent.objects.filter(reg_event__event = id, reg_event__bike_type__pk__in = [9, 4, 1]).order_by("-finish") #.values("fname", "lname", "sex", "nickname", "start_number", "status",  "resultevent__kp1", "resultevent__finish", "resultevent__start",  "pk", 'id', 'email', 'phone', 'city', 'birthday', 'club', 'bike_type', 'pay', 'description').order_by("date") #all rider list
    if revent.exclude(kp2 = None):
        kp2 = True
    if revent.exclude(kp3 = None):
        kp3 = True
    event_date = evt.date
    
    revent_road = ResultEvent.objects.filter(reg_event__event = id, reg_event__bike_type__pk__in = [9, 4, 1]).order_by("-finish")    
    cat1_b = event_date.year-19
    cat1_e = event_date.year-29
    revent_cat1 = revent_road.filter(reg_event__event = id, reg_event__birthday__year__lte = cat1_b, reg_event__birthday__year__gte = cat1_e, reg_event__start_status = True).order_by("-finish") #all rider list
    
    cat2_b = event_date.year-30
    cat2_e = event_date.year-39
    revent_cat2 = revent_road.filter(reg_event__event = id, reg_event__birthday__year__lte = cat2_b, reg_event__birthday__year__gte = cat2_e, reg_event__start_status = True).order_by("-finish") #all rider list
    
    cat3_b = event_date.year-40
    cat3_e = event_date.year-49
    revent_cat3 = revent_road.filter(reg_event__event = id, reg_event__birthday__year__lte = cat3_b, reg_event__birthday__year__gte = cat3_e, reg_event__start_status = True).order_by("-finish") #all rider list
    
    cat4_b = event_date.year-50
    cat4_e = event_date.year-59
    revent_cat4 = revent_road.filter(reg_event__event = id, reg_event__birthday__year__lte = cat4_b, reg_event__birthday__year__gte = cat4_e, reg_event__start_status = True).order_by("-finish") #all rider list

    cat5_b = event_date.year-60
    cat5_e = event_date.year-69
    revent_cat5 = revent_road.filter(reg_event__event = id, reg_event__birthday__year__lte = cat5_b, reg_event__birthday__year__gte = cat5_e, reg_event__start_status = True).order_by("-finish") #all rider list
    
    cat6_b = event_date.replace(year = event_date.year-70)
    revent_cat6 = revent_road.filter(reg_event__event = id, reg_event__birthday__year__lte = cat6_b.date().year, reg_event__start_status = True).order_by("-finish") #all rider list
    
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'event_rider_result.html', 'sel_menu': 'calendar', 'list': revent, 'entry': get_funn(), 'gcity': ResultEvent.group_city.filter(reg_event__event = id), 'cat1': revent_cat1, 'cat2': revent_cat2, 'cat3': revent_cat3, 'cat4': revent_cat4, 'cat5': revent_cat5, 'cat6': revent_cat6, 'kp2': kp2, 'kp3': kp3, 'uat':True}    
    evnt = {'event': evt}
    vars.update(evnt)
    try:
        del request.session['reg_email']
    except:
        error = "Параметр reg_email не існує"
    try:
        return render(request, 'index.html', vars)
    except:
        return HttpResponse("Результатів ще не має", content_type='text/plain;charset=utf-8')


def event_result_simple(request, id, point=None, full=None):
    revent_res = None
    evt = Events.objects.get(pk=id)
    username = request.user.username
    if point <> None:
        username = point
    #ResultEvent.objects.filter(reg_event__event = id).update(kp1=None, kp2=None)
    res = None
    if full == None:
        res = ResultEvent.objects.filter(reg_event__event = id).exclude(start=None).values('reg_event__start_number', 'reg_event__id').order_by('kp1')
    if full == True:
        res = ResultEvent.objects.filter(reg_event__event = id).values('reg_event__start_number', 'reg_event__id').order_by('kp1')
    start_count = res.count()    

    revent = None
    r_count = None
    ttable = dict
    if username == 'kp1' or point == 'kp1':
        if full == True:
            revent = ResultEvent.objects.filter(reg_event__event = id, kp1 = None).order_by("reg_event__start_number")
            revent_res = ResultEvent.objects.filter(reg_event__event = id).exclude(kp1 = None).order_by("reg_event__start_number")
        else:
            revent = ResultEvent.objects.filter(reg_event__event = id, kp1 = None).exclude(start=None).order_by("reg_event__start_number") 
            revent_res = ResultEvent.objects.filter(reg_event__event = id).exclude(kp1 = None).order_by("reg_event__start_number")
            
            try:
                tmp = revent_res[0]
            except:
                pass
            
            if revent.count() == 0:
                txt_url = reverse('event-result-light-admin-offline', kwargs={'id': id, 'point': 'kp1'})
                vars = {'sel_menu': 'calendar', 'entry': get_funn(), 'error_data': 'Учасники ще не стартували!', 'offline': txt_url}
                return render(request, 'index.html', vars)
      
            for i in revent_res:
                tdelta = i.kp1 - tmp.kp1
                tmp = i
                i.tdelta = tdelta
            
#            txt_url = reverse('event-result-light-admin-offline', kwargs={'id': id, 'point': 'kp1'})
#            vars = {'sel_menu': 'calendar', 'entry': get_funn(), 'error_data': 'Учасники ще не стартували!', 'offline': txt_url}
#            return render(request, 'index.html', vars)
    if username == 'kp2' or point == 'kp2':
        if full == True:
            revent = ResultEvent.objects.filter(reg_event__event = id, kp2 = None).order_by("reg_event__start_number")
            revent_res = ResultEvent.objects.filter(reg_event__event = id).exclude(kp2 = None).order_by("kp2")
        else:
            revent = ResultEvent.objects.filter(reg_event__event = id, kp2 = None).exclude(kp1=None).order_by("kp1") #.values("fname", "lname", "sex", "nickname", "start_number", "status",  "resultevent__kp1", "resultevent__finish", "resultevent__start",  "pk", 'id', 'email', 'phone', 'city', 'birthday', 'club', 'bike_type', 'pay', 'description').order_by("date") #all rider list
            revent_res = ResultEvent.objects.filter(reg_event__event = id).exclude(kp2 = None).order_by("kp2")

            try:
                tmp = revent_res[0]
            except:
                pass
            
            if revent.count() == 0:
                txt_url = reverse('event-result-light-admin-offline', kwargs={'id': id, 'point': 'kp2'})
                vars = {'sel_menu': 'calendar', 'entry': get_funn(), 'error_data': 'Учасники ще не проїхали попереднє КП!', 'offline': txt_url}
                return render(request, 'index.html', vars)
      
            for i in revent_res:
                tdelta = i.kp1 - tmp.kp1
                tmp = i
                i.tdelta = tdelta

    if username == 'kp3' or point == 'kp3':
        if full == True:
            revent = ResultEvent.objects.filter(reg_event__event = id, kp3 = None).order_by("reg_event__start_number")
            revent_res = ResultEvent.objects.filter(reg_event__event = id).order_by("reg_event__start_number")
        else:
            revent = ResultEvent.objects.filter(reg_event__event = id, kp3 = None).exclude(kp3=None).order_by("kp2") #.values("fname", "lname", "sex", "nickname", "start_number", "status",  "resultevent__kp1", "resultevent__finish", "resultevent__start",  "pk", 'id', 'email', 'phone', 'city', 'birthday', 'club', 'bike_type', 'pay', 'description').order_by("date") #all rider list
            revent_res = ResultEvent.objects.filter(reg_event__event = id).exclude(kp3 = None).order_by("kp3")

            try:
                tmp = revent_res[0]
            except:
                pass
            
            if revent.count() == 0:
                txt_url = reverse('event-result-light-admin-offline', kwargs={'id': id, 'point': 'kp2'})
                vars = {'sel_menu': 'calendar', 'entry': get_funn(), 'error_data': 'Учасники ще не проїхали попереднє КП!', 'offline': txt_url}
                return render(request, 'index.html', vars)
      
            for i in revent_res:
                tdelta = i.kp1 - tmp.kp1
                tmp = i
                i.tdelta = tdelta
                
    if username == 'finish' or point == 'finish':
        if full == True:
            revent = ResultEvent.objects.filter(reg_event__event = id, finish = None).order_by("reg_event__start_number")
            revent_res = ResultEvent.objects.filter(reg_event__event = id).order_by("reg_event__start_number")
        
        if ResultEvent.objects.filter(reg_event__event = id).exclude(kp2 = None):
            revent = ResultEvent.objects.filter(reg_event__event = id, finish = None).exclude(kp2=None).order_by("kp2")
        if ResultEvent.objects.filter(reg_event__event = id).exclude(kp3 = None):
            revent = ResultEvent.objects.filter(reg_event__event = id, finish = None).exclude(kp3=None).order_by("kp3")
        revent_res = ResultEvent.objects.filter(reg_event__event = id).exclude(finish = None).order_by("finish")       

    try:
        r_count = revent_res.count()
    except:
        r_count = 0

    vars = {'weblink': 'event_simple_result.html', 'sel_menu': 'calendar', 'list': revent, 'list_res': revent_res, 'uname': username, 's_count': start_count, 'r_count': r_count}
    evnt = {'event': evt}
    vars.update(evnt)
    #return render(request, 'index_result.html', vars)
    return render(request, 'index.html', vars)
    #return render_to_response('index_result.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))

            
@csrf_exempt
def result_add(request):
#    if (auth_group(request.user, 'admin') or auth_group(request.user, 'volunteer')) == False:
#        return HttpResponse("У вас не достатньо повноважень для даної функції", content_type="text/plain")
    if request.is_ajax() or request.method == 'POST':
        if request.method == 'POST':  
            POST = request.POST  
            if (POST.has_key('rid') and POST.has_key('chkhash')) or (auth_group(request.user, 'admin') or auth_group(request.user, 'volunteer')):
                rid = request.POST['rid']
                val = request.POST['value'].strip()
                point = request.POST['point']
                chkhash = None
                if (auth_group(request.user, 'admin') or auth_group(request.user, 'volunteer')) == False:
                    chkhash = request.POST['chkhash']
                else:
                    chkhash = 'Rivelo256haSh+123-2019'
                if chkhash <> 'Rivelo256haSh+123-2019':
                    return HttpResponseBadRequest('hash not found or invalid')
                rev = None
                try:
                    rev = RegEvent.objects.get(pk = rid)
                except RegEvent.DoesNotExist:
                    HttpResponse("Такого Id "+ rid +" не має в базі", content_type='text/plain')
                try:
                    rider = ResultEvent.objects.get(reg_event__pk = rid)
                    format = '%Y-%m-%d %H:%M:%S'
                    tp = datetime.datetime.now().strftime("%Y-%m-%d")
                    if val == '':
                        val = datetime.datetime.now().strftime("%H:%M:%S")
                    time_point = "%s %s" % (tp, val)
                    if val == '0':
                        time_point = None
                    if (val == 'DNF') or (val == 'dnf'):
                        point = 'dnf' 
                    #rider.kp1 = datetime.strptime(time_kp, format)
                    if point == 'start':
                        rider.start = time_point#datetime.datetime.now()
                        rider.save()
                    if point == 'kp1':
                        rider.kp1 = time_point#datetime.datetime.now()
                        rider.save()
                    if point == 'kp2':
                        rider.kp2 = time_point#datetime.datetime.now()
                        rider.save()
                    if point == 'finish':
                        rider.finish = time_point
                        rider.save()
                        rider = ResultEvent.objects.get(reg_event__pk = rid)                        
                        message = rev.event.email_text % (rider.get_time_diff())
                    if point == 'dnf':
                        rider.finish = rider.start
                        rider.save()
    #===========================================================================
    #                     """Вітаємо вас на фініші марафону Медовий трейл!\n 
    # Ви подолали маршрут за %s .\n\n
    # Запрошуємо вас 11 серпня відвідати наш грунтовий марафон "100 миль" \n
    # Інформацію по заходу можна знайти за посиланням  http://www.rivelo.com.ua/event/20/show/ \n
    # Список зареєстрованих знаходиться за цим посиланням http://www.rivelo.com.ua/event/20/registration/list/ \n
    # Гарних покатеньок і до зустрічі на старті.
    # """ 
    #===========================================================================

# Відправка результатів на пошту    
#                        res = send_mail('марафон Рівно100 2019 року. Результат', message, rider.reg_event.email, [rider.reg_event.email], fail_silently=False)

                    return HttpResponse("Час додано " + val , content_type='text/plain')
                except ObjectDoesNotExist:
                #rider = None
                #if rider == None:
                    r = ResultEvent()
                    r.reg_event = rev
                    if point == 'kp1':
                        r.kp1 = datetime.datetime.now()
                    if point == 'kp2':
                        r.kp1 = datetime.datetime.now()
                    if point == 'kp3':
                        r.kp1 = datetime.datetime.now()
                    if point == 'finish':
                        rider.finish = datetime.datetime.now()                      
                    r.save()
#                rider.start_status = not rider.start_status
#                rider.save()
#                json = dict(status = rider.start_status)
#                return HttpResponse(simplejson.dumps(json), content_type='application/json')
                    return HttpResponse("Невірні параметри запиту rid=" + rid + "val=" + val, content_type='text/plain')
                #else:
                #    r.reg_event = rev    
    return HttpResponse("Щось пішло не так :(", content_type='text/plain;charset=utf-8')        


@csrf_exempt
def result_add_lviv(request):
#    if (auth_group(request.user, 'admin') or auth_group(request.user, 'volunteer')) == False:
#        return HttpResponse("У вас не достатньо повноважень для даної функції", content_type="text/plain")
    if request.is_ajax() or request.method == 'POST':
        if request.method == 'POST':  
            POST = request.POST  
            if (POST.has_key('rid') and POST.has_key('chkhash')) or (auth_group(request.user, 'admin') or auth_group(request.user, 'volunteer')):
                rid = request.POST['rid']
                val = request.POST['value'].strip()
                point = request.POST['point']
                evn = request.POST['event']
                chkhash = None
                if (auth_group(request.user, 'admin') or auth_group(request.user, 'volunteer')) == False:
                    chkhash = request.POST['chkhash']
                else:
                    chkhash = 'Rivelo256haSh+123-2019'
                if chkhash <> 'Rivelo256haSh+123-2019':
                    return HttpResponseBadRequest('hash not found or invalid')
                rev = None
                try:
                    rev = RegEvent.objects.get(start_number = rid, event__pk = evn)
                except RegEvent.DoesNotExist:
                    HttpResponse("Такого номеру "+ rid +" не має в базі", content_type='text/plain')
                try:
                    rider = ResultEvent.objects.get(reg_event__pk = rev.pk)
                    format = '%Y-%m-%d %H:%M:%S'
                    tp = datetime.datetime.now().strftime("%Y-%m-%d")
                    if val == '':
                        val = datetime.datetime.now().strftime("%H:%M:%S")
                    time_point = "%s %s" % (tp, val)
                    #rider.kp1 = datetime.strptime(time_kp, format)
                    if point == 'start':
                        rider.start = time_point#datetime.datetime.now()
                        rider.save()
                    if point == 'kp1':
                        rider.kp1 = time_point#datetime.datetime.now()
                        rider.save()
                    if point == 'kp2':
                        rider.kp2 = time_point#datetime.datetime.now()
                        rider.save()
                    if point == 'finish':
                        rider.finish = time_point
                        rider.save()
                        rider = ResultEvent.objects.get(reg_event__pk = rid)                        
                        message = rev.event.email_text % (rider.get_time_diff())
                        res = send_mail('марафон Рівно100 2019 року. Результат', message, rider.reg_event.email, [rider.reg_event.email], fail_silently=False)

                    return HttpResponse("Час додано " + val , content_type='text/plain')
                except ObjectDoesNotExist:
                    r = ResultEvent()
                    r.reg_event = rev
                    if point == 'kp1':
                        r.kp1 = datetime.datetime.now()
                    if point == 'kp2':
                        r.kp1 = datetime.datetime.now()
                    if point == 'finish':
                        rider.finish = datetime.datetime.now()                      
                    r.save()
                    return HttpResponse("Невірні параметри запиту rid=" + rid + "val=" + val, content_type='text/plain')
                #else:
                #    r.reg_event = rev    
    return HttpResponse("Щось пішло не так :(", content_type='text/plain;charset=utf-8') 


@csrf_exempt
def rider_regstatus(request, id=None):
#    if (auth_group(request.user, 'admin') or auth_group(request.user, 'volunteer')) == False:
#        return HttpResponse("У вас не достатньо повноважень для даної функції", content_type="text/plain")
    if request.is_ajax() or request.method == 'POST':
        if request.method == 'POST':  
            POST = json.loads(request.body)
            if (('rid' in POST) and ('chkhash' in POST)) or (auth_group(request.user, 'admin') or auth_group(request.user, 'volunteer')):
                rid = POST['rid']
                chkhash = None
                if (auth_group(request.user, 'admin') or auth_group(request.user, 'volunteer')) == False:
                    #chkhash = request.POST['chkhash']
                    chkhash = POST['chkhash']
                else:
                    chkhash = settings.CHK_APP_HASH #'Rivelo256haSh+1234567890-2019'
                if chkhash <> settings.CHK_APP_HASH: #'Rivelo256haSh+1234567890-2019':
                    return HttpResponseBadRequest('hash not found or invalid')
                rev = None
                try:
                    rev = RegEvent.objects.get(pk = rid)
                    #return HttpResponse("Учасник - " + rid + ". Номер  " + rid.start_number + "Pay status = " + rid.status, content_type='text/plain')
                    
                    json_data = dict(rider = rev.fname + " " + rev.lname, pay_status = rev.status, status = rev.start_status, start_number = rev.start_number, event=rev.event.name)
                    return HttpResponse(simplejson.dumps(json_data), content_type='application/json')
            
                except RegEvent.DoesNotExist:
                    return HttpResponse("Id "+ rid +" is not found", content_type='text/plain')
    else:
        #obj_qr = '<img src="{{1244|qr:"500x500"}}" />'
        obj_qr = '<img src="http://chart.apis.google.com/chart?chs=500x500&cht=qr&chl='+str(id)+'&choe=UTF-8&chld=H|0"/>'
        return HttpResponse("You QR code for quick registration <br> " + obj_qr, content_type='text/html;charset=utf-8')
#    return HttpResponse("Щось пішло не так :(", content_type='text/plain;charset=utf-8')       
    return HttpResponse("Щось пішло не так", content_type='text/plain;charset=utf-8')


@csrf_exempt
def result_remove(request):
    if (auth_group(request.user, 'admin') or auth_group(request.user, 'volunteer')) == False:
        return HttpResponse("У вас не достатньо повноважень для даної функції", content_type="text/plain")
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('rid'):
                rid = request.POST['rid']
                point = request.POST['point']
                try:
                    rider = ResultEvent.objects.get(pk = rid)
                    if point == 'kp1':
                        val = rider.kp1
                        rider.kp1 = None
                    if point == 'kp2':
                        val = rider.kp2
                        rider.kp2 = None
                    if point == 'finish':
                        val = rider.finish
                        rider.finish = None
                    rider.save()
                    return HttpResponse("Час видалено " +str(val), content_type='text/plain')
                except ObjectDoesNotExist:
                    return HttpResponse("Часова відмітка відсутня" + str(val), content_type='text/plain')
    return HttpResponse("Щось пішло не так :(", content_type='text/plain')        
    

@csrf_exempt
def result_date_normalize(request):
    if auth_group(request.user, 'admin')==False:
        return HttpResponse("У вас не достатньо повноважень для даної функції", content_type="text/plain")
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('date'):
                val = request.POST['date']
                try:
                    ev = request.POST['event']
                    evt = Events.objects.get(pk = ev)
                    riders = ResultEvent.objects.filter(reg_event__event = evt, start__date__gt = evt.date.date())
                    for rider in riders:
                        rider.start = datetime.datetime.combine(evt.date.date(), rider.start.time())
#                        rider.kp1 = datetime.datetime.combine(evt.date(), rider.kp1.time())
#                        rider.kp1 = datetime.datetime.combine(evt.date(), rider.kp2.time())
#                        rider.kp3 = datetime.datetime.combine(evt.date(), rider.kp3.time())
#                        rider.finish = datetime.datetime.combine(evt.date(), rider.finish.time())
                        #rider.start = evt.date
                        rider.save()
                    riders = ResultEvent.objects.filter(reg_event__event = evt, finish__date__gt = evt.date.date())
                    for rider in riders:
                        rider.finish = datetime.datetime.combine(evt.date.date(), rider.finish.time())
                        rider.save()
                         
                    #===========================================================
                    # riders.update(kp1 = None)
                    # riders.update(kp2 = None)
                    # riders.update(kp3 = None)
                    # riders.update(finish = None)
                    # riders.update(start = None)
                    #===========================================================
                    return HttpResponse("Час видалено" + val, content_type='text/plain')
                except ObjectDoesNotExist:
                    return HttpResponse("Час не видалено", content_type='text/plain')
    return HttpResponse("Щось пішло не так :(", content_type='text/plain')        


@csrf_exempt
def result_clear(request):
    if auth_group(request.user, 'admin')==False:
        return HttpResponse("У вас не достатньо повноважень для даної функції", content_type="text/plain")
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('point'):
                val = request.POST['point']
                try:
                    ev = request.POST['event']
                    evt = Events.objects.get(pk = ev)
                    riders = ResultEvent.objects.filter(reg_event__event=evt)
                    if val == 'kp1':
                        riders.update(kp1=None)
                    if val == 'kp2':
                        riders.update(kp2=None)
                    if val == 'finish':
                        riders.update(finish=None)
                    if val == 'result':
                        riders.delete()
                    return HttpResponse("Час видалено" + val, content_type='text/plain')
                except ObjectDoesNotExist:
                    return HttpResponse("Час не видалено", content_type='text/plain')
    return HttpResponse("Щось пішло не так :(", content_type='text/plain')        


@csrf_exempt
def event_start(request):
    if auth_group(request.user, 'admin')==False:
        return HttpResponse("У вас не достатньо повноважень для даної функції", content_type="text/plain")
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('event'):
                val = request.POST['value']
                try:
                    ev = request.POST['event']
                    evt = Events.objects.get(pk = ev)
                    riders = ResultEvent.objects.filter(reg_event__status = True, reg_event__start_status = True, reg_event__event=evt)
                    #riders = ResultEvent.objects.all()
                    format = '%Y-%m-%d %H:%M:%S'
                    tp = datetime.datetime.now().strftime("%Y-%m-%d")                    
                    #time_point = "2017-05-28 %s" % (val)
                    time_point = "%s %s" % (tp, val)
                    if val == '' or val == None:
                       time_point = datetime.datetime.now()
                    #uriders = riders.filter(start__isnull=False)
                    uriders = riders
                    uriders.update(start=time_point)
                    
                    #riders = RegEvent.objects.filter(status = True, start_status = False, resultevent__start = None, event=evt)
                    eres = ResultEvent.objects.filter(reg_event__status = True, reg_event__start_status = False, reg_event__event=evt)
                    eres.update(start=None)
                    
                    riders_dns = RegEvent.objects.filter(status = True, start_status = False, event=evt).exclude(resultevent__in = eres)
                    for rider in riders_dns: 
                        r = ResultEvent(reg_event=rider, start = None)
                        r.save()

                    riders = RegEvent.objects.filter(status = True, start_status = True, event=evt).exclude(resultevent__in = uriders)                    
                    for rider in riders:
                    #    if eres:
                    #        eres.start = time_point
                    #        eres.save()
                    #    else:
                        r = ResultEvent(reg_event=rider, start=time_point)
                        r.save()                            
                    
                    #riders = RegEvent.objects.filter(status = True, start_status = False, event=evt)
                    
                    return HttpResponse("Час додано" + val, content_type='text/plain')
                
                except ObjectDoesNotExist:
                    return HttpResponse("Час не додано", content_type='text/plain')
                
    return HttpResponse("Щось пішло не так :(", content_type='text/plain')        
    

def show_client(request, user_name='rivno100'):
    if auth_group(request.user, 'admin')==False:
        #vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'error_data': 'У вас не вистачає повноважень!'}
        vars = {'sel_menu': 'calendar', 'error_data': 'У вас не вистачає повноважень, або ви не увійшли на портал!'}
        return render(request, 'index.html', vars)
#        return HttpResponse("У вас не достатньо повноважень для даної функції", content_type="text/plain")
    client = None
    c_invoice = None
    if user_name == 'med':
        client = Client.objects.get(pk = 2533) # medov trail
        c_invoice = ClientInvoice.objects.filter(client__pk = 2533, pay = False) #2533 - медовий трейл / 2010 - поліська січ
    if user_name == 'rivno100':        
        client = Client.objects.get(pk = 1943) # rivno100
        c_invoice = ClientInvoice.objects.filter(client__pk = 1943, pay = False, date__year = datetime.datetime.today().year) #2533 - медовий трейл / 2010 - поліська січ
    if user_name == 'pol_sich':        
        client = Client.objects.get(pk = 2010) # поліська січ
        c_invoice = ClientInvoice.objects.filter(client__pk = 2010, pay = False) #2533 - медовий трейл / 2010 - поліська січ
    if user_name == '100mile':        
        client = Client.objects.get(pk = 2615) # 100 миль
        c_invoice = ClientInvoice.objects.filter(client__pk = 2615, pay = False) #2533 - медовий трейл / 2010 - поліська січ
    vars = {'weblink': 'shop_client.html', 'sel_menu': 'calendar', 'list': c_invoice, }    
    evnt = {'client': client}
    vars.update(evnt)
    try:
        del request.session['reg_email']
    except:
        error = "Параметр reg_email не існує"
    return render(request, 'index.html', vars)
    #return render_to_response('index_result.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))        
#    return HttpResponse("Клієнт << " + cl.name, content_type='text/plain')


@csrf_exempt
def client_sale(request):
    if auth_group(request.user, 'admin')==False:
        return HttpResponse("У вас не достатньо повноважень для даної функції", content_type="text/plain")
    if request.is_ajax():
        if request.method == 'POST':  
            POST = request.POST  
            if POST.has_key('cid'):
                cid = request.POST['cid']
                val = request.POST['value']
                c_id = request.POST['client']
                cat = Catalog.objects.get(pk = cid)
                #client = Client.objects.get(pk = 2010)
                client = Client.objects.get(pk = c_id)
                ci = ClientInvoice()
                ci.client = client
                ci.catalog = cat
                ci.count = int(val)
                ci.price = cat.price
                ci.sum = float(cat.price) * float(val)
                ci.pay = float(cat.price) * float(val)
                ci.currency_id = 3
                ci.date = datetime.datetime.now()
                ci.save()
#                try:
#                    return HttpResponse("Час додано" + val, content_type='text/plain')
#                except ObjectDoesNotExist:

                return HttpResponse("Продано "+ val +" шт.", content_type='text/plain')
                #else:
                #    r.reg_event = rev    
    return HttpResponse("Щось пішло не так :(", content_type='text/plain')


def event_rider_copy(request, id, evnt=None):
    if auth_group(request.user, 'moder')==False:
        return HttpResponse("У вас не достатньо повноважень для даної функції")
    res = RegEvent.objects.filter(pk = id)
#    evt = Events.objects.get(pk = evnt)    
#    new_object = RegEvent(event = evt, fname=revent.fname, lname=revent.lname, sex=revent.sex, nickname=revent.nickname, email=revent.email, phone=revent.phone, country=revent.country, city=revent.city, club=revent.club, bike_type=revent.bike_type, birthday=revent.birthday)
#    new_object.save()
    vars = html_content_right()
    
    if res.filter(event__pk = evnt) :
        message = "Ви вже зареєстровані на даний захід"
        #return HttpResponse(message)
        vars.update({'success_data': message, 'reglist': reverse('event-rider-list' , kwargs={'id':evnt})})
        return render(request, 'index.html', vars)
    
    if res:
        clone = res[0]  
        clone.pk = None
        clone.event = Events.objects.get(pk = evnt)
        clone.date = datetime.datetime.now()
        clone.start_number = 0
        clone.description = ""
        clone.pay_type = null
        clone.pay = 0
        clone.pay_date = None
        clone.status = False
        clone.start_status = False
        clone.save()
        reg_code = hashlib.sha256(str(clone.pk)).hexdigest()
        clone.reg_code = reg_code
        send_reg_mail(request, clone.pk, clone.email, "Редагування даних")
    else:
        message = "Поштової адреси та телефону не знайдено"
        return HttpResponse(message, content_type='text/plain')
   
#    return HttpResponse("Щось пішло не так :(", content_type='text/plain')            
    return HttpResponseRedirect(reverse('event-rider-list', args=[evnt]))


def rider_search(request):
    if request.user.is_authenticated()==False and auth_group(request.user, 'admin')==False:
        return HttpResponse("<h2>Для виконання операції, авторизуйтесь</h2>", content_type="text/plain;charset=utf-8")
    message = "Шукаємо текст "
    if request.method == 'POST':  
        POST = request.POST  
        if POST.has_key('rider_s'):
            rider_s = request.POST.get( 'rider_s' )
            photo1 = Photo.objects.random()
            photo2 = Photo.objects.random()
            #list = RegEvent.objects.filter(lname__icontains = rider_s)
            list = RegEvent.objects.filter(Q(lname__icontains = rider_s) | Q(fname__icontains = rider_s) | Q(phone__icontains=rider_s) | Q(nickname__icontains=rider_s))
            message = message + rider_s
            #return HttpResponse(message, content_type="text/plain;charset=utf-8")
            vars = {'weblink': 'regevent_search_edit_table.html', 'sel_menu': 'calendar', 'list': list, 'search_str': rider_s, 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'default_domain': settings.DEFAULT_DOMAIN}
            calendar = embeded_calendar()
            vars.update(calendar)        

            #return render_to_response('index_result.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))
        #    return render(request, 'index_result.html', vars)
            return render(request, 'index.html', vars)
        
    return HttpResponse(message, content_type="text/plain;charset=utf-8")

    #return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))


@csrf_exempt
def rider_reg_search(request):
    if request.is_ajax():
        if request.method == 'POST':
            POST = request.POST
            res = None
            if POST.has_key('email') or POST.has_key('phone'):
                mail = request.POST.get('email')
                p = request.POST.get('phone')
                if mail:
                    res = RegEvent.objects.filter(email__iregex=r'^'+mail+'$' ).values_list('email', 'event__name')
                if p:
                    res = RegEvent.objects.filter(phone__iregex=r'^'+'\\' + p + '$').values_list('email', 'event__name')
                if res:
                    json_data = list([1, res[0]])
                    return HttpResponse(simplejson.dumps(json_data), content_type='application/json')
                    #return HttpResponse(res[0])
                else:
                    message = "Поштової адреси та телефону не знайдено"
                    json_data = list([0, message]) 
                    return HttpResponse(simplejson.dumps(json_data), content_type='application/json')                    
#                    return HttpResponse(message, content_type="text/plain;charset=utf-8")
    message = "Щось пішло не так"
    json_data = list([0, message]) 
    return HttpResponse(simplejson.dumps(json_data), content_type='application/json')    
    #return HttpResponse(message, content_type="text/plain;charset=utf-8")


def rider_reg_copy(request, id):
    res = None
    vars = html_content_right()
    if request.method == 'POST':
        POST = request.POST

        if POST.has_key('email') or POST.has_key('phone'):
            mail = request.POST.get('email')
            p = request.POST.get('phone')
            if mail:
                res = RegEvent.objects.filter(email__iregex=r'^'+mail+'$' )
            if p:
                res = RegEvent.objects.filter(phone__iregex=r'^'+'\\' + p + '$')
            if res.filter(event__pk = id) :
                message = "Ви вже зареєстровані на даний захід"
                #return HttpResponse(message)
                vars.update({'success_data': message, 'reglist': reverse('event-rider-list' , kwargs={'id':id})})
                return render(request, 'index.html', vars)
            
            if res:
                clone = res[0]  
                clone.pk = None
                clone.save()
                clone.event = Events.objects.get(pk = id)
                clone.date = datetime.datetime.now()
                clone.start_number = 0
                clone.description = ""
                reg_code = hashlib.sha256(str(clone.pk)).hexdigest()
                clone.reg_code = reg_code
                clone.pay_type = null
                clone.pay = 0
                clone.pay_date = None
                clone.status = False
                clone.start_status = False
                 
                clone.save()
                send_reg_mail(request, clone.pk, clone.email, "Редагування даних")
            else:
                message = "Поштової адреси та телефону не знайдено"
                return HttpResponse(message)

    message = 'Ви зареєструвались на ' + res[0].event.name
    vars.update({'success_data': message, 'reglist': reverse('event-rider-list' , kwargs={'id':id})})
    return render(request, 'index.html', vars)
#    return HttpResponse('Ви зареєструвались на ' + res[0].event.name)


def rider_reg_delete(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponse('Error: У вас не має прав для редагування')
    rider = RegEvent.objects.get(pk = id)
    ev = rider.event.pk
    rider.delete()
    return HttpResponseRedirect(reverse('event-rider-list' , kwargs={'id':ev}))

@csrf_exempt
def regevent_edit(request, id=None):
    if auth_group(request.user, 'admin')==False:
        return HttpResponse('Error: У вас не має прав для редагування')

    if request.is_ajax():
        if request.method == 'POST':
            POST = request.POST
            
            if POST.has_key('rid') and POST.has_key('fname'):
                id = request.POST.get('rid')
                d = request.POST.get('fname')
                obj = RegEvent.objects.get(id = id)
                obj.fname = d.strip()
                obj.save() 
                c = RegEvent.objects.filter(id = id).values_list('fname', flat=True)
                return HttpResponse(c)

            if POST.has_key('rid') and POST.has_key('lname'):
                id = request.POST.get('rid')
                d = request.POST.get('lname')
                obj = RegEvent.objects.get(id = id)
                obj.lname = d.strip()
                obj.save() 
                c = RegEvent.objects.filter(id = id).values_list('lname', flat=True)
                return HttpResponse(c)

            if POST.has_key('rid') and POST.has_key('nickname'):
                id = request.POST.get('rid')
                d = request.POST.get('nickname')
                obj = RegEvent.objects.get(id = id)
                obj.nickname = d.strip()
                obj.save() 
                c = RegEvent.objects.filter(id = id).values_list('nickname', flat=True)
                return HttpResponse(c)

            if POST.has_key('rid') and POST.has_key('city'):
                id = request.POST.get('rid')
                d = request.POST.get('city')
                obj = RegEvent.objects.get(id = id)
                obj.city = d.strip()
                obj.save() 
                c = RegEvent.objects.filter(id = id).values_list('city', flat=True)
                return HttpResponse(c)

            if POST.has_key('rid') and POST.has_key('phone'):
                id = request.POST.get('rid')
                d = request.POST.get('phone')
                obj = RegEvent.objects.get(id = id)
                obj.phone = d.strip()
                obj.save() 
                c = RegEvent.objects.filter(id = id).values_list('phone', flat=True)
                return HttpResponse(c)

            if POST.has_key('rid') and POST.has_key('email'):
                id = request.POST.get('rid')
                d = request.POST.get('email')
                obj = RegEvent.objects.get(id = id)
                obj.email = d.strip()
                obj.save() 
                c = RegEvent.objects.filter(id = id).values_list('email', flat=True)
                return HttpResponse(c)

            if POST.has_key('rid') and POST.has_key('birthday'):
                id = request.POST.get('rid')
                d = request.POST.get('birthday')
                d2 = datetime.datetime.strptime(d.strip(),'%d/%m/%Y').strftime('%Y-%m-%d')
                obj = RegEvent.objects.get(id = id)
                obj.birthday = d2
                obj.save() 
                c = RegEvent.objects.filter(id = id).values_list('birthday', flat=True)
                return HttpResponse(c)


    message = "Щось пішло не так" 
    return HttpResponse(message, content_type="text/plain;charset=utf-8")


def year_results(request, year=2017):   
    id = 4
    evt = Events.objects.get(pk=id)
    events = Events.objects.filter(date__year = year, reg_status = True).order_by('date')
    evt_ids = events.values('id')
    revent = ResultEvent.objects.filter(reg_event__event__in = evt_ids, finish__isnull=False).order_by("reg_event__lname", "-finish") #.values("fname", "lname", "sex", "nickname", "start_number", "status",  "resultevent__kp1", "resultevent__finish", "resultevent__start",  "pk", 'id', 'email', 'phone', 'city', 'birthday', 'club', 'bike_type', 'pay', 'description').order_by("date") #all rider list
    #stat_res = revent.values('reg_event__phone', 'reg_event__fname', 'reg_event__lname', ).order_by('reg_event__phone').distinct() # annotate(cphone = Count('reg_event__phone')) #.distinct('')
    #stat_res = revent.values('reg_event__fname', 'reg_event__lname', 'reg_event__phone', 'reg_event__birthday').annotate(cphone = Count('reg_event__phone')).order_by("-cphone") #.distinct('')
    #stat_res = revent.values('reg_event__lname', 'reg_event__fname', 'reg_event__phone',).annotate(cphone = Count('reg_event')).order_by("-cphone")
    stat_res = revent.order_by('reg_event__phone')#.values('reg_event__phone', 'reg_event__fname', 'reg_event__lname', 'reg_event__birthday', 'reg_event__city', 'reg_event__event', 'reg_event__event__name', 'reg_event__club', 'finish')    
    event_date = evt.date
    male = ResultEvent.male_objects.get_male_byyear(year)
    #male = revent.active_for_account(1).count()
    female = ResultEvent.female_objects.get_female_byyear(year)
    #print "FEMALE  = ", female
    #female = revent.active_for_account(0).count()
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    
    vars = {'weblink': 'summary_year_results.html', 'sel_menu': 'calendar', 'entry': get_funn(), 'gphoto1': photo1, 'gphoto2': photo2, 'list': revent, 'events': events, 'male':male, 'female':female, 'stat_res': stat_res, 'year': year}    
    evnt = {'event': evt}
    vars.update(evnt)
    try:
        del request.session['reg_email']
    except:
        error = "Параметр reg_email не існує"
    #return render_to_response('index_result.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))
    #return render(request, 'index_result.html', vars)        
    return render(request, 'index.html', vars)
#    pass
#    return HttpResponse("Щось пішло не так :(", content_type='text/plain;charset=utf-8')


def shop_bicycle_company(request):
    #bsc = Bicycle_Store.objects.filter(count__gte = 1).values('model__brand__logo', 'model__brand', 'model__brand__name', 'model__brand__id').annotate(brand_c = Count('model__brand'))
    bs_brand_list = Bicycle_Store.objects.filter(count__gte = 1).values_list('model__brand', flat=True) #values('model__brand')#.annotate(dcount=Count('model__brand')) #.annotate(brand_c = Count('model__brand__pk'))
    m_list = list(set(bs_brand_list))
    #m_list = [19, 1, 3, 68, 197, 199, 138, 11, 179, 155]
    bsc = Manufacturer.objects.filter(pk__in = m_list).order_by('name')    
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'bicycles_company_list.html', 'sel_menu': 'shop', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'bicycle_companys': bsc, 'default_domain': settings.DEFAULT_DOMAIN}
    calendar = embeded_calendar()
    vars.update(calendar)        
    #return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))
    return render(request, 'index.html', vars)        


def shop_bicycle_brand(request, id=None, sale=None):
    id = id
    bsb = Bicycle_Store.objects.filter(count__gte = 1, model__brand__pk = id)
    if sale:
        bsb = bsb.filter(model__sale__gt = 0)
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'bicycles_list_bybrand.html', 'sel_menu': 'shop', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'bicycle_bybrand': bsb, 'sale_status': sale, 'default_domain': settings.DEFAULT_DOMAIN}
    calendar = embeded_calendar()
    vars.update(calendar)        
    #return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))
    return render(request, 'index.html', vars)        


def shop_bicycle_type(request, type=None):
#    type = None
    if type:
        typeid = Bicycle_Type.objects.filter(id = type)
    else:
        typeid = Bicycle_Type.objects.filter(id = 8) #Kids
    bst = Bicycle_Store.objects.filter(count__gte = 1, model__type__pk = typeid)
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'bicycles_list_bytype.html', 'sel_menu': 'shop', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'bicycle_bytype': bst, 'default_domain': settings.DEFAULT_DOMAIN}
    calendar = embeded_calendar()
    vars.update(calendar)        
    return render(request, 'index.html', vars)        


def shop_bicycle(request, id):
    id = id
    bs = Bicycle_Store.objects.get(id = id)
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'bicycles_list.html', 'sel_menu': 'shop', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'bicycle': bs, 'default_domain': settings.DEFAULT_DOMAIN}
    calendar = embeded_calendar()
    vars.update(calendar)        
    #return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))
    return render(request, 'index.html', vars)        


def shop_company_list(request):
    scc = Catalog.objects.filter(count__gte = 1) #.values('manufacturer__logo', 'name', 'manufacturer__name', 'manufacturer__id', 'type')
    scc = scc.values('manufacturer__id', 'manufacturer__logo', 'manufacturer__name', 'manufacturer__id').distinct().annotate(brand_c = Count('manufacturer__id')).order_by('manufacturer__name') #annotate(brand_c = Count('manufacturer__id'))
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'components_type_list.html', 'sel_menu': 'shop', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'components_company': scc, 'default_domain': settings.DEFAULT_DOMAIN}
    calendar = embeded_calendar()
    vars.update(calendar)        
    #return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))
    return render(request, 'index.html', vars)        


def shop_type_list(request):
#    scc = Catalog.objects.filter(count__gte = 1) #.values('manufacturer__logo', 'name', 'manufacturer__name', 'manufacturer__id', 'type')
#    scc = scc.values('type__id', 'type__name', 'type__name_ukr', 'type__description_ukr').distinct().annotate(type_c = Count('type__id')).order_by('type__name') #annotate(brand_c = Count('manufacturer__id'))
    scc = Type.objects.all()
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'components_type_list.html', 'sel_menu': 'shop', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'components_list_bytype': scc, 'default_domain': settings.DEFAULT_DOMAIN}
    calendar = embeded_calendar()
    vars.update(calendar)        
    return render(request, 'index.html', vars)        


def shop_components_brand(request, id):
    scb = Catalog.objects.filter(count__gte = 1, manufacturer__id = id).order_by('type') #.values('manufacturer__logo', 'name', 'manufacturer__name', 'manufacturer__id', 'type')
    #scc = scc.values('manufacturer__id', 'manufacturer__logo', 'manufacturer__name', 'manufacturer__id').distinct().annotate(brand_c = Count('manufacturer__id')).order_by('manufacturer__id') #annotate(brand_c = Count('manufacturer__id'))
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'components_list.html', 'sel_menu': 'shop', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'components_list': scb, 'status_brand': True, 'default_domain': settings.DEFAULT_DOMAIN}
    calendar = embeded_calendar()
    vars.update(calendar)        
    #return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))
    return render(request, 'index.html', vars)        
    

def shop_components_brand_sale(request, id):
    scb = Catalog.objects.filter(count__gte = 1, manufacturer__id = id, sale__gt = 0).order_by('type') #.values('manufacturer__logo', 'name', 'manufacturer__name', 'manufacturer__id', 'type')
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'components_list.html', 'sel_menu': 'shop', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'components_list': scb, 'status_brand': True, 'default_domain': settings.DEFAULT_DOMAIN}
    calendar = embeded_calendar()
    vars.update(calendar)        
    return render(request, 'index.html', vars)        


def shop_components_type(request, id):
    sct = Catalog.objects.filter(count__gte = 1, type__id = id) #.values('manufacturer__logo', 'name', 'manufacturer__name', 'manufacturer__id', 'type')
    #scc = scc.values('manufacturer__id', 'manufacturer__logo', 'manufacturer__name', 'manufacturer__id').distinct().annotate(brand_c = Count('manufacturer__id')).order_by('manufacturer__id') #annotate(brand_c = Count('manufacturer__id'))
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'components_list.html', 'sel_menu': 'shop', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'components_list': sct, 'status_type': True,  'default_domain': settings.DEFAULT_DOMAIN}
    calendar = embeded_calendar()
    vars.update(calendar)        
    #return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))
    return render(request, 'index.html', vars)        


def shop_components_type_sale(request, id):
    sct = Catalog.objects.filter(count__gte = 1, type__id = id, sale__gt = 0) 
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'components_list.html', 'sel_menu': 'shop', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'components_list': sct, 'status_type': True,  'default_domain': settings.DEFAULT_DOMAIN}
    calendar = embeded_calendar()
    vars.update(calendar)        
    return render(request, 'index.html', vars)        


def shop_component(request, id):
    sc = Catalog.objects.get(id = id) #.values('manufacturer__logo', 'name', 'manufacturer__name', 'manufacturer__id', 'type')
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'component_view.html', 'sel_menu': 'shop', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'component': sc, 'default_domain': settings.DEFAULT_DOMAIN}
    calendar = embeded_calendar()
    vars.update(calendar)        
    #return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))
    return render(request, 'index.html', vars)        


def shop_components_sale(request):
    scs = Catalog.objects.filter(count__gt = 0, sale__gt = 0).order_by('-sale')    
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'components_sale_list.html', 'sel_menu': 'shop', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'components_sale': scs, 'default_domain': settings.DEFAULT_DOMAIN}
    calendar = embeded_calendar()
    vars.update(calendar)        
    return render(request, 'index.html', vars)        
    

def shop_main(request):
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'shop_main.html', 'sel_menu': 'shop', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'default_domain': settings.DEFAULT_DOMAIN}
    calendar = embeded_calendar()
    vars.update(calendar)        
    #return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))
    return render(request, 'index.html', vars)        


def shop_search(request):
#    if request.user.is_authenticated()==False and auth_group(request.user, 'admin')==False:
#        return HttpResponse("<h2>Для виконання операції, авторизуйтесь</h2>", content_type="text/plain;charset=utf-8")
    message = "Шукаємо текст "
    if request.method == 'GET':  
        POST = request.GET  
        if POST.has_key('rider_s'):
            rider_s = request.GET.get( 'rider_s' )
            photo1 = Photo.objects.random()
            photo2 = Photo.objects.random()
            scs = Catalog.objects.filter(Q(ids__icontains = rider_s) | Q(dealer_code__icontains = rider_s) | Q(name__icontains = rider_s)).exclude(count = 0).order_by('-sale')
            message = message + rider_s
            vars = {'weblink': 'components_list.html', 'sel_menu': 'shop', 'search_str': rider_s, 'components_list': scs, 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'default_domain': settings.DEFAULT_DOMAIN}
            calendar = embeded_calendar()
            vars.update(calendar)        
            return render(request, 'index.html', vars)
        
    return HttpResponse(message, content_type="text/plain;charset=utf-8")


def workshop_main(request):
    wg = WorkGroup.objects.all().order_by('tabindex')
#    WorkType.objects.filter()
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'workshop_main.html', 'sel_menu': 'workshop', 'workgroup': wg,  'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'default_domain': settings.DEFAULT_DOMAIN}
    calendar = embeded_calendar()
    vars.update(calendar)        
    return render(request, 'index.html', vars)        


def workshop_service(request):
    wg = WorkGroup.objects.all().order_by('tabindex')
    service_work = WorkType.objects.get(pk = 649)
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'workshop_service.html', 'sel_menu': 'workshop', 'serv_work': service_work, 'workgroup': wg, 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'default_domain': settings.DEFAULT_DOMAIN}
    calendar = embeded_calendar()
    vars.update(calendar)        
    return render(request, 'index.html', vars)        


def shop_discount(request):
    curr_date = datetime.date.today()
    d_list = Discount.objects.filter(date_start__lte = curr_date, date_end__gte = curr_date).order_by('type_id')
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'discount_list.html', 'sel_menu': 'workshop', 'd_list': d_list, 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'default_domain': settings.DEFAULT_DOMAIN}
    calendar = embeded_calendar()
    vars.update(calendar)        
    return render(request, 'index.html', vars)        


def routes_list(request):
    r_list = Route.objects.all()
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'routes.html', 'sel_menu': 'other', 'routes': r_list, 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'default_domain': settings.DEFAULT_DOMAIN}
    calendar = embeded_calendar()
    vars.update(calendar)        
    return render(request, 'index.html', vars)        


def video_list(request):
    youtube_list = YouTube.objects.all().order_by('-date') #values('url').distinct()
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'video_list.html', 'sel_menu': 'other', 'youtube_list': youtube_list, 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'default_domain': settings.DEFAULT_DOMAIN}
    calendar = embeded_calendar()
    vars.update(calendar)        
    return render(request, 'index.html', vars)        
    
        

import csv
from django.template import loader, Context

def csv_view(request, id, start=True):
    if auth_group(request.user, 'admin')==False:
        return HttpResponse('Error: У вас не має прав для скачування файлу')
    
    if start == True:
        revent = RegEvent.objects.filter(event = id, start_status = True).order_by("date") #all rider list
    else:
        revent = RegEvent.objects.filter(event = id).order_by("date") #all rider list

# Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

    writer = csv.writer(response)
#    writer.writerow(['chip', 'prizv', 'Name', 'rid', 'phone'])

    for item in revent:
        writer.writerow([item.start_number+1000, item.lname, item.fname, item.id, item.phone, item.start_number])
#    writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
#    writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])
    return response


def csv_reg_list_view(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponse('Error: У вас не має прав для скачування файлу')
    
#    revent = RegEvent.objects.filter(event = id, start_number__gt = 0 ).order_by("date") #all rider list
    revent = RegEvent.objects.filter(event = id, status = True ).order_by("date") #all rider list

# Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="number_list.csv"'

    writer = csv.writer(response)
#    writer.writerow(['chip', 'prizv', 'Name', 'rid', 'phone'])

    for item in revent:
        rname = item.lname +" "+ item.fname
        gender = "M"
        if item.sex == 1:
            gender = "M"
        else:
            gender = "F" 
        category = item.category_uat()
#        print "cat type = " + str(type(category))
        
        writer.writerow([item.start_number, rname, gender, item.club, category, item.phone, item.id, item.nickname])

    return response


def csv_result_list_uat(request, id):
    if auth_group(request.user, 'admin')==False:
        return HttpResponse('Error: У вас не має прав для скачування файлу')
    revent = ResultEvent.objects.filter(reg_event__event = id, reg_event__bike_type__pk__in = [9, 4, 1]).order_by("finish") 
#    revent = RegEvent.objects.filter(event = id, status = True ).order_by("date") #all rider list

# Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="result_list_uat.csv"'

    writer = csv.writer(response)

    for item in revent:
        rname = item.reg_event.lname +" "+ item.reg_event.fname
        gender = "M"
        if item.reg_event.sex == 1:
            gender = "M"
        else:
            gender = "F" 
        category = item.reg_event.category_uat()
        writer.writerow([item.reg_event.start_number, rname, gender, item.reg_event.club, category, item.reg_event.nickname, item.reg_event.bike_type.name, item.start, item.finish, item.get_time_diff()])

    return response

