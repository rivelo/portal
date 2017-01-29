# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpRequest, HttpResponseNotFound
from django.conf import settings

from portal.event_calendar.views import embeded_calendar
from portal.funnies.views import get_funn
from models import News, Comments
from portal.news.forms import NewsForm

from portal.gallery.models import Album, Photo
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
    news = News.objects.all().order_by('-pk')
    vars = {'weblink': 'main.html', 'sel_menu': 'main', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'news': news}
    calendar = embeded_calendar()
    vars.update(calendar)
    
    paginator = Paginator(news, 3)
    page = request.GET.get('page')
    if page == None:
        page = 1
    try:
        news = paginator.page(page)
#        vars.update(news)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        news = paginator.page(1)
#        vars.update(news)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        news = paginator.page(paginator.num_pages)
    vars.update({'news': news})
    
    return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))


def add_news(request):
    if request.user.is_authenticated()==False:
        return HttpResponse("<h2>Для виконання операції, авторизуйтесь</h2>")
    a = News()
    if request.method == 'POST':
        form = NewsForm(request.POST, instance=a)
        if form.is_valid():
            title = form.cleaned_data['title']
            text = form.cleaned_data['text']
#            date = form.cleaned_data['date']
            link = form.cleaned_data['link']
            author = form.cleaned_data['author']
            category = form.cleaned_data['category']
            comm = form.cleaned_data['comments']
#            user = form.cleaned_data['user']
            n = News(title=title, text=text, date=datetime.datetime.now(), link=link, author=author, category=category, user=request.user)
            #n.comments.add(comm)
            n.save()
            return HttpResponseRedirect('/')
    else:
        form = NewsForm(instance=a, initial={'author': request.user })
    
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'news_add.html', 'sel_menu': 'main', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'form': form}
    calendar = embeded_calendar()
    vars.update(calendar)
    return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))


def edit_news(request, id):
    if request.user.is_authenticated()==False:
        return HttpResponse("<h2>Для виконання операції, авторизуйтесь</h2>")
    a = News.objects.get(pk=id)
    if request.method == 'POST':
        form = NewsForm(request.POST, instance=a)
        if form.is_valid():
            title = form.cleaned_data['title']
            text = form.cleaned_data['text']
            link = form.cleaned_data['link']
            author = form.cleaned_data['author']
            category = form.cleaned_data['category']
            comm = form.cleaned_data['comments']
            a.title=title
            a.text=text
            a.date=a.date
            a.link=link
            a.author=author
            a.category=category
            a.user=request.user
            a.save()
            return HttpResponseRedirect('/')
    else:
        form = NewsForm(instance=a)
    
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    vars = {'weblink': 'news_add.html', 'sel_menu': 'main', 'photo1': photo1, 'photo2': photo2, 'entry': get_funn(), 'form': form}
    calendar = embeded_calendar()
    vars.update(calendar)
    return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))


def delete_news(request, id):
    obj = News.objects.get(id=id)
    if request.user == obj.user:
        obj.delete()
    if (auth_group(request.user, 'admin') == False):
        return HttpResponse("У вас не має прав на видалення. Зверніться до адміністратора")
    obj.delete()
    return HttpResponseRedirect('/')


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
    
