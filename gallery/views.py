# -*- coding: utf-8 -*-

from django.http import HttpResponse
#from django.shortcuts import render_to_response
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpRequest, HttpResponseNotFound
from django.conf import settings

from portal.event_calendar.views import embeded_calendar
from portal.funnies.views import get_funn
from models import Album, Photo

import gdata.photos.service
import gdata.media
import gdata.geo


def custom_proc(request):
# "A context processor that provides 'app', 'user' and 'ip_address'."
    return {
        'app': 'Rivelo catalog',
        'user': request.user,
        'ip_address': request.META['REMOTE_ADDR']
    }

def get_album():
    list = []
    album_list = []
    gd_client = gdata.photos.service.PhotosService()
    gd_client.email = "velorivne@gmail.com"
    gd_client.password = "gvelovelo"
    gd_client.source = 'velorivne_albums'
    gd_client.ProgrammaticLogin()
    username = "velorivne@gmail.com"
    albums = gd_client.GetUserFeed(user=username)
    for album in albums.entry:
        print 'title: %s, number of photos: %s, id: %s' % (album.title.text, album.numphotos.text, album.gphoto_id.text)
        album_list.append(album.title.text)
        photos = gd_client.GetFeed('/data/feed/api/user/%s/albumid/%s?kind=photo' % (username, album.gphoto_id.text))
        for photo in photos.entry:
            print 'Photo title:', photo.title.text
            list.append(photo.content.src)
    return list, album_list


def albums_page(request):
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    albums = Album.objects.all() 
    vars = {'weblink': 'photo.html', 'sel_menu': 'photo', 'photo1': photo1, 'photo2': photo2, 'albums': albums, 'entry': get_funn()}
    calendar = embeded_calendar()
    vars.update(calendar)
    return render(request, 'index.html', vars)        
    #return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))


def album_page(request, id):
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
    album = Album.objects.get(album_id=id)
    album_name = album.title + " - " + str(album.numphotos) + " фото"
    photos = Photo.objects.filter(album = album) 
    vars = {'weblink': 'photo_album.html', 'sel_menu': 'photo', 'photo1': photo1, 'photo2': photo2, 'album_name': album_name, 'photos': photos, 'entry': get_funn()}
    calendar = embeded_calendar()
    vars.update(calendar)        
    #return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))
    return render(request, 'index.html', vars)


def gallery_page(request):
    photo1 = Photo.objects.random()
    photo2 = Photo.objects.random()
#    p_list, albums = get_album()
    albums = Album.objects.all() 
    p_list = Photo.objects.filter(album = albums[3])
    vars = {'weblink': 'photo.html', 'sel_menu': 'photo', 'photo_list': p_list[:10], 'photo1': photo1, 'photo2': photo2, 'albums': albums}
    calendar = embeded_calendar()
    vars.update(calendar)
    #p_list = p_list[:10]
#    return render_to_response('index.html', {'weblink': 'photo.html', 'sel_menu': 'photo', 'photo_list': p_list[:10], 'albums': albums}, context_instance=RequestContext(request, processors=[custom_proc]))
    #return render_to_response('index.html', vars, context_instance=RequestContext(request, processors=[custom_proc]))
    return render(request, 'index.html', vars)


def create_db(request):
    username = 'rivelo2010@gmail.com'
    gd_client = gdata.photos.service.PhotosService()
    albums = gd_client.GetUserFeed(user=username)
    for album in albums.entry:
        print 'title: %s, number of photos: %s, id: %s' % (album.title.text, album.numphotos.text, album.gphoto_id.text)
        try:
            alb = Album(title=album.title.text, url=album.GetHtmlLink().href, numphotos=album.numphotos.text, album_id=album.gphoto_id.text)
            alb.save()
        except:
            # do not duplicate albums
            pass    
        photos = gd_client.GetFeed('/data/feed/api/user/%s/albumid/%s?kind=photo' % (username, album.gphoto_id.text))
        for photo in photos.entry:
            print 'Photo title:', photo.title.text
            try:
                p = Photo(album=alb, title=photo.title.text, image=photo.media.thumbnail[2].url, url=photo.content.src, pub_date=photo.timestamp.datetime(), filename=photo.media.title.text, photo_id=photo.gphoto_id.text, height=int(photos.entry[0].height.text), width=int(photos.entry[0].width.text))
                p.save()
            except:
                # do not duplicate albums
                pass
    
    return HttpResponse("Дані додано")    
