# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from django.conf import settings

from django.contrib.auth import views as auth_views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from portal.news import views as news_views
from portal.gallery import views as gallery_views
from portal.event_calendar import views as event_calendar_views

from django.views.static import serve

urlpatterns = [ #patterns('',
    # Examples:
    # url(r'^$', 'portal.views.home', name='home'),
    # url(r'^portal/', include('portal.foo.urls')),

    #(r'^$', 'news_views.views.get_news', {'count_on_page':2} ),
    url(r'^$', news_views.main_page, name='home'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^settings/$', news_views.settings, name='settings'),
    url(r'^settings/password/$', news_views.password, name='password'),
    url(r'^oauth/', include('social_django.urls', namespace='social')),  # <--
    url(r'^news/add/$', news_views.add_news ),
    url(r'^news/(?P<id>\d+)/edit/$', news_views.edit_news ),
    url(r'^news/(?P<id>\d+)/delete/$', news_views.delete_news ),
    url(r'^news/result/(?P<year>\d+)/$', event_calendar_views.year_results, name='year-result' ),
    url(r'^contact/$', news_views.contact_page ),
    url(r'^about/$', news_views.about_page),
    url(r'^photo/$', gallery_views.albums_page ),
    url(r'^photo/album/(?P<id>\d+)/$', gallery_views.album_page),
    url(r'^photo/create/db/$', gallery_views.create_db ),
    url(r'^accounts/login/$',  news_views.login),
    url(r'^accounts/logout/$', news_views.logout),
    url(r'^calendar/year/(?P<year>\d+)/month/(?P<month>\d+)/$', event_calendar_views.calendar_filter),
    url(r'^calendar/year/(?P<year>\d+)/$', event_calendar_views.calendar_filter, name='calendar-year'),
    url(r'^calendar/$', event_calendar_views.calendar_page),
    url(r'^event/getdate/$', event_calendar_views.get_event),
    url(r'^event/add/$', event_calendar_views.add_event),
    url(r'^event/(?P<id>\d+)/edit/$', event_calendar_views.edit_event),
    url(r'^event/(?P<id>\d+)/show/$', event_calendar_views.show_event, name='event-show'),
    url(r'^event/(?P<id>\d+)/result/$', event_calendar_views.event_result, name='event-result'),
    url(r'^event/result/clear/$', event_calendar_views.result_clear, name='event-result-clear'),
    url(r'^event/(?P<id>\d+)/result/simple/$', event_calendar_views.event_result_simple, name='event-result-light'),
    url(r'^event/(?P<id>\d+)/result/(?P<point>\w+)/simple/$', event_calendar_views.event_result_simple, name='event-result-light-admin'), 
    url(r'^rider/result/add/$', event_calendar_views.result_add, name='event-result-add'),
    url(r'^rider/result/remove/$', event_calendar_views.result_remove, name='event-result-remove'),
    url(r'^event/registration/(?P<hash>[A-Fa-f0-9]{64})/$', event_calendar_views.register_to_all, name='other-event-registration'),
    url(r'^rider/start/edit/$', event_calendar_views.event_start, name='event-start'),
    url(r'^event/(?P<id>\d+)/registration/$', event_calendar_views.add_reg, name='event-registration'),
    url(r'^event/(?P<id>\d+)/registration/list/$', event_calendar_views.event_reg_list, name='event-rider-list'),
    url(r'^event/(?P<id>\d+)/registration/edit/number/$', event_calendar_views.event_reg_edit, name='event-rider-edit-number'),
    url(r'^event/(?P<id>\d+)/start/list/$', event_calendar_views.event_reg_list, {'start' : True}, name='event-start-list'),
    url(r'^event/gps/get/$', event_calendar_views.get_event_gps),
    url(r'^event/rider/(?P<id>\d+)/info/$', event_calendar_views.get_event_rider, name='event-rider-info'),
    url(r'^event/rider/(?P<id>\d+)/pay/(?P<hash>[A-Fa-f0-9]{64})/$', event_calendar_views.add_rider_pay, name='rider-pay-submit'),
    url(r'^event/rider/(?P<id>\d+)/pay/$', event_calendar_views.add_rider_pay, name='rider-pay-submit-admin'),
    url(r'^event/rider/(?P<id>\d+)/registration/(?P<hash>[A-Fa-f0-9]{64})/edit/$', event_calendar_views.edit_reg, name='event-registration-edit'),
    url(r'^rider/registration/$', event_calendar_views.event_rider_status),
    url(r'^rider/(?P<id>\d+)/registration/copy/$', event_calendar_views.event_rider_copy, name='rider-reg-copy'),
    url(r'^rider/(?P<id>\d+)/registration/copy/(?P<evnt>\d+)/to/$', event_calendar_views.event_rider_copy, name='rider-reg-copy-to'),
    url(r'^rider/startstatus/$', event_calendar_views.rider_start_status),
    url(r'^rider/(?P<id>\d+)/send/reminder/mail/$', event_calendar_views.admin_sendmail, name='rider-reminder-mail'),
    url(r'^rider/(?P<id>\d+)/send/invite/mail/$', event_calendar_views.admin_invite_mail, name='rider-invite-mail'),
    url(r'^rider/(?P<id>\d+)/send/invite/mail/(?P<evnt>\d+)/to/$', event_calendar_views.admin_invite_mail, name='rider-invite-mail-to'),
#    url(r'^wheel/size/add/$', portal.toolsadd_wheelsize' ),
    url(r'^rider/search/$', event_calendar_views.rider_search, name='rider-search'),
    url(r'^rider/registration/search/$', event_calendar_views.rider_reg_search, name='rider-reg-search'),
    url(r'^registration/edit/$', event_calendar_views.regevent_edit),
    url(r'^rider/registration/(?P<id>\d+)/send/$', event_calendar_views.rider_reg_copy), #copy old registration by rider
    url(r'^rider/registration/(?P<id>\d+)/delete/$', event_calendar_views.rider_reg_delete, name='rider-reg-delete'), # delete registratiion
    url(r'^rider/edit/email/$', event_calendar_views.regevent_edit), # change email
    

    url(r'^shop/$', event_calendar_views.shop_main, name='shop-main'),
    url(r'^components/$', event_calendar_views.shop_components_company, name='components-company'),
    url(r'^components/sale/$', event_calendar_views.shop_components_sale, name='components-sale'),
    url(r'^components/(?P<id>\d+)/brand/$', event_calendar_views.shop_components_brand, name='components-list-bybrand'),
    url(r'^components/(?P<id>\d+)/type/$', event_calendar_views.shop_components_type, name='components-list-bytype'),
    url(r'^component/(?P<id>\d+)/$', event_calendar_views.shop_component, name='component-show'),
    url(r'^bicycles/$', event_calendar_views.shop_bicycle_company, name='bicycle-company'),
    url(r'^bicycles/(?P<id>\d+)/brand/$', event_calendar_views.shop_bicycle_brand, name='bicycle-list-bybrand'),
    url(r'^bicycles/(?P<id>\d+)/model/$', event_calendar_views.shop_bicycle, name='bicycle-show'),
#    url(r'^client/$', event_calendar_viewsshow_client'),
    url(r'^client/sale/$', event_calendar_views.client_sale),
    url(r'^client/(?P<user_name>[A-Za-z0-9_]+)/$', event_calendar_views.show_client),
    
    url(r'^location/$', event_calendar_views.google_location),
#    url(r'^prod/$', portal.tools.view_product'),
    url(r'^tinymce/', include('tinymce.urls')),

    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
]


if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})
    ]