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