# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.conf import settings


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'portal.views.home', name='home'),
    # url(r'^portal/', include('portal.foo.urls')),

    #(r'^$', 'portal.news.views.get_news', {'count_on_page':2} ),
    url(r'^$', 'portal.news.views.main_page' ),
    url(r'^news/add/$', 'portal.news.views.add_news' ),
    url(r'^news/(?P<id>\d+)/edit/$', 'portal.news.views.edit_news' ),
    url(r'^news/(?P<id>\d+)/delete/$', 'portal.news.views.delete_news' ),
    url(r'^contact/$', 'portal.news.views.contact_page' ),
    url(r'^about/$', 'portal.news.views.about_page' ),
    url(r'^photo/$', 'portal.gallery.views.albums_page' ),
    url(r'^photo/album/(?P<id>\d+)/$', 'portal.gallery.views.album_page'),
    url(r'^photo/create/db/$', 'portal.gallery.views.create_db' ),
    url(r'^accounts/login/$',  'portal.news.views.login'),
    url(r'^accounts/logout/$', 'portal.news.views.logout'),
    url(r'^calendar/year/(?P<year>\d+)/month/(?P<month>\d+)/$', 'portal.event_calendar.views.calendar_filter'),
    url(r'^calendar/year/(?P<year>\d+)/$', 'portal.event_calendar.views.calendar_filter'),
    url(r'^calendar/$', 'portal.event_calendar.views.calendar_page'),
    url(r'^event/getdate/$', 'portal.event_calendar.views.get_event'),
    url(r'^event/add/$', 'portal.event_calendar.views.add_event'),
    url(r'^event/(?P<id>\d+)/edit/$', 'portal.event_calendar.views.edit_event'),
    url(r'^event/(?P<id>\d+)/registration/$', 'portal.event_calendar.views.add_reg', name='event-registration'),
    url(r'^event/(?P<id>\d+)/registration/list/$', 'portal.event_calendar.views.event_reg_list', name='event-rider-list'),
    url(r'^event/gps/get/$', 'portal.event_calendar.views.get_event_gps'),
    url(r'^event/rider/(?P<id>\d+)/info/$', 'portal.event_calendar.views.get_event_rider', name='event-rider-info'),
    url(r'^event/rider/(?P<id>\d+)/pay/(?P<hash>[A-Fa-f0-9]{64})/$', 'portal.event_calendar.views.add_rider_pay', name='rider-pay-submit'),
    url(r'^location/$', 'portal.event_calendar.views.google_location'),
    url(r'^tinymce/', include('tinymce.urls')),

    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)


if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))