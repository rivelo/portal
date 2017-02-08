# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response
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

from models import Events, RegEvent
from forms import EventsForm, RegEventsForm, PayRegEventsForm

from portal.gallery.models import Album, Photo
from portal.funnies.views import get_funn

import simplejson
import googlemaps

from portal.mysql_portal import get_month_event, get_month_events, get_day_events


def portal_sendmail(to, subject, message):
    from_mail = settings.EMAIL_HOST_USER #settings.DEFAULT_FROM_EMAIL  
    #to = ['rivelo@ymail.com',]  
    #subject = ''  

    email_text = """\
    From: %s  
    To: %s  
    Subject: %s
    %s
    """ % (from_mail, ", ".join(to), subject, message)

    try:  
        server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.ehlo()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.sendmail(from_mail, to, email_text)
        server.close()
        return ('ok', 'Лист успішно відправлено')
    except:  
        return ('error', 'Щось пішло не так')


def send_reg_mail(request, rid, mto):
    revent = RegEvent.objects.get(pk = rid)
    w = render_to_response('event_rider_info.html', {'rider': revent, 'thismail' : True})
    subject = 'Реєстрація'  
    from_email = 'rivno100@gmail.com' 
    to = mto
    text_content = 'www.rivelo.com.ua'
    html_content = w.content
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return render_to_response("index.html", {'success_data': "Лист відправлено на пошту" + to}, context_instance=RequestContext(request, processors=[custom_proc]))


def email_two(rid, mto):
    subject = "I am an HTML email"
    to = [mto]
    from_email = 'rivno100@gmail.com'
    revent = RegEvent.objects.get(pk = rid)
    ctx = {
        'rider': revent, 
        'thismail' : True
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

#    return {'weeks': month_calendar, 'events': get_month_event(year, month),
    return {'weeks': month_calendar, 'sel_day': today, 'sel_date': selected_date, 
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
                elist = Events.objects.filter(date__year = date_y, date__month = date_m, date__day = date_d).values("name", "text", "type", "icon", "date", "photo", "user__username", "pub_date", "forum_url", "reg_url", "pk")
                json = list(elist)
                for x in json:  
                    x['date'] = x['date'].strftime("%d/%m/%Y")
                    x['pub_date'] = x['pub_date'].strftime("%d/%m/%Y")
                #json = serializers.serialize('json', p_cred_month, fields=('id', 'date', 'price', 'description', 'user', 'user_username'))
                return HttpResponse(simplejson.dumps(json), content_type='application/json')
    
    return HttpResponse(elist, content_type='application/json')        


#from django.contrib.auth.models import User

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
               
            evt = Events(name=name, text=text, url=url, reg_url=reg_url, reg_status=reg_status, photo=photo, icon=icon, forum_url=forum_url, lat=lat, lng=lng, description=description, date=date, city=city, user = user)
            evt.save()
#            if reg_status == True:
#                reg_url = "/event/"+ str(evt.pk) +"/registration/"
#            evt.reg_url = reg_url
            
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


def show_event(request, id):
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'event_show.html', 'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn()}
    calendar = embeded_calendar()
    vars.update(calendar)        
    event = Events.objects.get(pk = id)
    evnt = {'event': event}
    vars.update(evnt)
    return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))    
    

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
#    r = RegEvent()
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    calendar = embeded_calendar()
    if request.method == 'POST':
        form = RegEventsForm(request.POST, instance=r)
        gresp = {} 
        gr = grecaptcha_verify(request)
        if gr['status'] == False:
            vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'error_data': 'Пройдіть підтвердження що ви не робот'}
            vars.update(calendar)        
            evnt = {'event': a}
            vars.update(evnt)
            return render(request, 'index.html', vars)
            
            # https://developers.google.com/recaptcha/docs/verify
        if form.is_valid():
#            event = form.cleaned_data['event']
            fname = form.cleaned_data['fname']
            lname = form.cleaned_data['lname']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            country = form.cleaned_data['country']
            city = form.cleaned_data['city']
            club = form.cleaned_data['club']
            bike_type = form.cleaned_data['bike_type']
            birthday = form.cleaned_data['birthday']
            #pay = form.cleaned_data['pay']
            #date = form.cleaned_data['date']
            #status = form.cleaned_data['status']
            description = form.cleaned_data['description']
            event = a
            
            regevt = RegEvent(event=event, fname=fname, lname=lname, email=email, phone=phone, country=country, city=city, club=club, bike_type=bike_type, birthday=birthday, description = description)
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
            
            return HttpResponseRedirect('/event/rider/'+str(regevt.pk)+'/info/')
    else:
        form = RegEventsForm(instance=r)
        
    vars = {'weblink': 'event_reg_add.html', 'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'form': form}
    vars.update(calendar)        
    evnt = {'event': a}
    vars.update(evnt)
    return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))        


def event_reg_list(request, id):
    evt = Events.objects.get(pk=id)
    revent = RegEvent.objects.filter(event = id).order_by("date") #all rider list
    curyear = datetime.datetime.now().year
    cat1_b = curyear-18
    cat1_e = curyear-29
#    revent_cat1 = RegEvent.objects.filter(event = id, birthday__gt = datetime.date(cat1_b, 1, 1), birthday__lt = datetime.date(cat1_e, 1, 1)).order_by("date") #all rider list
    revent_cat1 = RegEvent.objects.filter(event = id, birthday__range=[datetime.date(cat1_e, 1, 1), datetime.date(cat1_b, 12, 31)])
    cat2_b = curyear-30
    cat2_e = curyear-39
    revent_cat2 = RegEvent.objects.filter(event = id, birthday__lte = datetime.date(cat2_b, 12, 31), birthday__gte = datetime.date(cat2_e, 1, 1)).order_by("date") #all rider list
    cat3_b = curyear-40
    cat3_e = curyear-49
    revent_cat3 = RegEvent.objects.filter(event = id, birthday__lte = datetime.date(cat3_b, 12, 31), birthday__gte = datetime.date(cat3_e, 1, 1)).order_by("date") #all rider list
    cat4_b = curyear-50
    cat4_e = curyear-59
    revent_cat4 = RegEvent.objects.filter(event = id, birthday__lte = datetime.date(cat4_b, 12, 31), birthday__gte = datetime.date(cat4_e, 1, 1)).order_by("date") #all rider list
    cat5_b = curyear-60
    revent_cat5 = RegEvent.objects.filter(event = id, birthday__lte = datetime.date(cat5_b, 1, 1)).order_by("date") #all rider list
    
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'event_reg_list.html', 'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'list': revent, 'cat1': revent_cat1, 'cat2': revent_cat2, 'cat3': revent_cat3, 'cat4': revent_cat4, 'cat5': revent_cat5}
    calendar = embeded_calendar()
    vars.update(calendar)        

    evnt = {'event': evt}
    vars.update(evnt)
   
    return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))        
    
    
def get_event_rider(request, id):
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
        return HttpResponse("У вашому браузері не працюють кукі/Cookie. ")
    
    revent = RegEvent.objects.get(pk = id)
    code = request.session.get("registrationcode")
    if not code:
#    if "registrationcode" in request.session : 
        return HttpResponse("Ваше посилання вже не є актуальним! model = " + revent.reg_code, content_type="text/plain")

    if request.session['registrationcode'] != revent.reg_code :
        return HttpResponse("Ваше посилання вже не є актуальним! model = " + revent.reg_code + "SESSION_ID = "+ request.COOKIES['sessionid'], content_type="text/plain")
    
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'event_rider_info.html', 'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'rider': revent}
    calendar = embeded_calendar()
    vars.update(calendar)        
    regmail = request.session.get("reg_email")
    if (not regmail) and (regmail != True):
        send_reg_mail(request, revent.pk, revent.email)
        res_data = "EMail надіслано"
        request.session['reg_email'] = True
    return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))        


def add_rider_pay(request, id, hash):
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    revent = RegEvent.objects.get(pk = id)    
    if hash != revent.reg_code:
        vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'error_data': 'Ваше посилання вже не є актуальним!'}
        return render(request, 'index.html', vars)
#    else:
#        vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'success_data': res_data}
#        return render(request, 'index.html', vars)
    if request.method == 'POST':
        form = PayRegEventsForm(request.POST, instance=revent)
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
            email_two(revent.pk, revent.email)
            vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'success_data': 'Дякуємо за внесені дані, після перевірки адміністрацією Вас буде відмічено на протязі доби'}
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
    
    return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))    

    