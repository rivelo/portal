# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'portal.views.home', name='home'),
    # url(r'^portal/', include('portal.foo.urls')),

    #(r'^$', 'portal.news.views.get_news', {'count_on_page':2} ),
    (r'^$', 'portal.news.views.main_page' ),
    (r'^contact/$', 'portal.news.views.contact_page' ),
    (r'^about/$', 'portal.news.views.about_page' ),
    (r'^photo/$', 'portal.gallery.views.albums_page' ),
    (r'^photo/album/(?P<id>\d+)/$', 'portal.gallery.views.album_page'),
    (r'^photo/create/db/$', 'portal.gallery.views.create_db' ),
    (r'^accounts/login/$',  'portal.news.views.login'),
    (r'^accounts/logout/$', 'portal.news.views.logout'),

    
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