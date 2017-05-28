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

from django.core.mail import send_mail


def admin_sendmail(request, id):
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    calendar = embeded_calendar()
    if auth_group(request.user, 'admin')==False:
        vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'error_data': 'У вас не вистачає повноважень!'}
        return render(request, 'index.html', vars)
    revent = RegEvent.objects.get(pk = id)
    csum = revent.event.cur_reg_sum()
    dleft = revent.event.days_left()
    
    message = """Нагадуємо що до заходу залишилось %s днів. \n 
    На даний момент реєстрація коштує %s гривень. Не затягуйте з оплатою адже чим ближче до заходу тим реєстраційний внесок більший.\n
    Оплату марафону можна здійснити: \n
    - на картку приватбанку (4323 3552 0025 8937 - Панчук Ігор) \n
    - оплатити в магазині Рівело (місто Рівне, вул.Кавказька 6) [http://www.rivelo.com.ua/about/] \n
    Інформацію по заходу можна знайти за посиланням  http://www.rivelo.com.ua/event/%s/show/ \n
    Список зареєстрованих знаходиться за цим посиланням http://www.rivelo.com.ua/event/%s/registration/list/ \n
    Гарних покатеньок і до зустрічі на старті.
    """ % (dleft, csum, revent.pk, revent.pk)
    
    res = send_mail('Нагадування про оплату', message, revent.email, ['rivelo@ymail.com'], fail_silently=False)
        
    if res == 1:
        return render_to_response("index.html", {'success_data': "Лист відправлено на пошту " + revent.email}, context_instance=RequestContext(request, processors=[custom_proc]))
    return render_to_response("index.html", {'success_data': "Щось пішло не так. Пошта " + revent.email}, context_instance=RequestContext(request, processors=[custom_proc]))

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
        w = render_to_response('event_rider_info.html', {'rider': revent, 'thismail' : True, 'default_domain': settings.DEFAULT_DOMAIN, 'main_text': 'Ви успішно відредагували свої дані на марафон ', 'event_rules': everules})
    else:
        w = render_to_response('event_rider_info.html', {'rider': revent, 'thismail' : True, 'default_domain': settings.DEFAULT_DOMAIN, 'main_text': 'Вітаємо ви успішно зареєструвались на марафон ', 'event_rules': everules })
    from_email = 'rivno100@gmail.com' 
    to = mto
    text_content = 'www.rivelo.com.ua'
    html_content = w.content
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return render_to_response("index.html", {'success_data': "Лист відправлено на пошту" + to}, context_instance=RequestContext(request, processors=[custom_proc]))


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
    res = gmaps.places_autocomplete("Рівн", language="uk", type='(regions)', components={'country': 'ua'})
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
               
            evt = Events(name=name, text=text, url=url, reg_url=reg_url, reg_status=reg_status, photo=photo, icon=icon, forum_url=forum_url, lat=lat, lng=lng, description=description, date=date, city=city, user = user)
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
            event = a
            
            regevt = RegEvent(event=event, fname=fname, lname=lname, nickname=nickname, email=email, phone=phone, country=country, city=city, club=club, bike_type=bike_type, birthday=birthday, sex=sex, description = description)
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
        form = RegEventsForm(instance=r)
        
    vars = {'weblink': 'event_reg_add.html', 'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'form': form}
    vars.update(calendar)        
    evnt = {'event': a}
    vars.update(evnt)
    return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))        


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
        form = RegEventsForm(request.POST, instance=revent)
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
        form = RegEventsForm(instance=revent)
        
    vars = {'weblink': 'event_reg_add.html', 'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'form': form}
    vars.update(calendar)        
    evnt = {'event': a}
    vars.update(evnt)
    return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))        


def event_reg_list(request, id):
    evt = Events.objects.get(pk=id)
    revent = RegEvent.objects.filter(event = id).order_by("date") #all rider list
    event_date = evt.date
    #curyear = datetime.datetime.now().year
    cat0_b = event_date.replace(year = event_date.year-12)
    cat0_e = event_date.replace(year = event_date.year-18)
    revent_cat0 = RegEvent.objects.filter(event = id, birthday__lte = cat0_b, birthday__gte = cat0_e.date).order_by("date") #all rider list
    cat1_b = event_date.replace(year = event_date.year-18)
    cat1_e = event_date.replace(year = event_date.year-30)
    #revent_cat1 = RegEvent.objects.filter(event = id, birthday__lte = datetime.date(1999, 1, 5), birthday__gte = datetime.date(1987, 1, 5)).order_by("date") #all rider list
    revent_cat1 = RegEvent.objects.filter(event = id, birthday__lte = cat1_b, birthday__gte = cat1_e.date).order_by("date") #all rider list
    #RegEvent.objects.filter(event = id, birthday__range=[cat1_e, cat1_b])
    cat2_b = event_date.replace(year = event_date.year-30)
    cat2_e = event_date.replace(year = event_date.year-40)
    revent_cat2 = RegEvent.objects.filter(event = id, birthday__lte = cat2_b, birthday__gte = cat2_e).order_by("date") #all rider list
    cat3_b = event_date.replace(year = event_date.year-40)
    cat3_e = event_date.replace(year = event_date.year-50)
    revent_cat3 = RegEvent.objects.filter(event = id, birthday__lte = cat3_b, birthday__gte = cat3_e).order_by("date") #all rider list
    cat4_b = event_date.replace(year = event_date.year-50)
    cat4_e = event_date.replace(year = event_date.year-60)
    revent_cat4 = RegEvent.objects.filter(event = id, birthday__lte = cat4_b, birthday__gte = cat4_e).order_by("date") #all rider list
    cat5_b = event_date.replace(year = event_date.year-60)
    revent_cat5 = RegEvent.objects.filter(event = id, birthday__lte = cat5_b).order_by("date") #all rider list
    
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'event_reg_list.html', 'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'list': revent, 'cat0': revent_cat0, 'cat1': revent_cat1, 'cat2': revent_cat2, 'cat3': revent_cat3, 'cat4': revent_cat4, 'cat5': revent_cat5}
    calendar = embeded_calendar()
    vars.update(calendar)        

    evnt = {'event': evt}
    vars.update(evnt)
    try:
        del request.session['reg_email']
    except:
        error = "Параметр reg_email не існує"
    return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))        
    
    
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
                res = RegEvent.objects.filter(event = chk_event, start_number__gt=0).values_list('start_number', flat=True).order_by('start_number')
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
    
    revent = RegEvent.objects.get(pk = id)
    code = request.session.get("registrationcode")
    if not code and auth_group(request.user, 'admin')==False:
#    if "registrationcode" in request.session : 
        return HttpResponse("Ваше посилання вже не є актуальним! model = " + revent.reg_code, content_type="text/plain")

    if request.session.get('registrationcode') != revent.reg_code and auth_group(request.user, 'admin')==False:
    #if request.session['registrationcode'] != revent.reg_code :
        return HttpResponse("Ваше посилання вже не є актуальним!!! model = " + revent.reg_code + "  SESSION_ID = "+ str(request.session.get('registrationcode'))+ "AUTH = " + str(auth_group(request.user, 'admin')), content_type="text/plain") 
                            #request.COOKIES['sessionid'], content_type="text/plain")
    everules = revent.event.rules.all()
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'event_rider_info.html', 'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'rider': revent, 'reg_ok': True, 'event_rules': everules}
    calendar = embeded_calendar()
    vars.update(calendar)        
    regmail = request.session.get("reg_email")
    if (not regmail) and (regmail != True):
        if request.session.get("registration_subject"):
            #request.session.get["registration_subject"]
            send_reg_mail(request, revent.pk, revent.email, "Редагування даних")
        else:
            send_reg_mail(request, revent.pk, revent.email)
        res_data = "EMail надіслано"
        request.session['reg_email'] = True
    return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))        


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
            #if (not paymail) and (paymail != True):
            try:
                email_two(revent.pk, revent.email)
            except:
                vars = {'sel_menu': 'calendar', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'error_data': 'Сталася помилка. Звяжіться з адміністратором rivno100@gmail.com'}
                return render(request, 'index.html', vars)
                
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
    return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))        


def test_func(request):
    revent = RegEvent.objects.get(pk = 15)
    everules = revent.event.rules.all()
    w = None
    if request.session.get("registration_subject"):
        pass
    else:
        w = render_to_response('event_rider_info.html', {'rider': revent, 'thismail' : True, 'default_domain': settings.DEFAULT_DOMAIN, 'main_text': 'Ви успішно відредагували свої дані на марафон ', 'event_rules': everules})
#    send_reg_mail(request, revent.pk, revent.email, "Редагування даних")
    return w


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
                json = dict(status = rider.status)
                return HttpResponse(simplejson.dumps(json), content_type='application/json')
    
    return HttpResponse("Щось пішло не так :(", content_type='text/plain')        
    