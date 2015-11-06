# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'rivelo_portal.views.home', name='home'),
    # url(r'^rivelo_portal/', include('rivelo_portal.foo.urls')),

    #(r'^$', 'rivelo_portal.news.views.get_news', {'count_on_page':2} ),
    (r'^$', 'rivelo_portal.news.views.main_page' ),
    (r'^contact/$', 'rivelo_portal.news.views.contact_page' ),
    (r'^about/$', 'rivelo_portal.news.views.about_page' ),
    (r'^photo/$', 'rivelo_portal.gallery.views.gallery_page' ),
    
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