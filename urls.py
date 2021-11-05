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
    url(r'^news/(?P<id>\d+)/show/$', news_views.show_news, name='news-show' ),
    url(r'^news/result/(?P<year>\d+)/$', event_calendar_views.year_results, name='year-result' ),
    url(r'^contact/$', news_views.contact_page ),
    url(r'^about/$', news_views.about_page),
    url(r'^photo/$', gallery_views.albums_page ),
    url(r'^photo/album/(?P<id>\d+)/$', gallery_views.album_page),
    url(r'^photo/create/db/$', gallery_views.create_db ),
    url(r'^accounts/login/$',  news_views.login),
    url(r'^accounts/logout/$', news_views.logout),
    url(r'^calendar/year/(?P<year>\d+)/month/(?P<month>\d+)/$', event_calendar_views.calendar_page),
    url(r'^calendar/year/(?P<year>\d+)/$', event_calendar_views.calendar_page, name='calendar-year'),
    url(r'^calendar/$', event_calendar_views.calendar_page),
    url(r'^event/getdate/$', event_calendar_views.get_event),
    url(r'^event/add/$', event_calendar_views.add_event),
    url(r'^event/(?P<id>\d+)/edit/$', event_calendar_views.edit_event),
    url(r'^rivno100/$', event_calendar_views.show_event, {'id': 25} , name='event-show'),
    url(r'^100mile/$', event_calendar_views.show_event, {'id': 34} , name='event-show'),
    url(r'^event/(?P<id>\d+)/show/$', event_calendar_views.show_event, name='event-show'),
    url(r'^event/(?P<id>\d+)/send/qr/code/$', event_calendar_views.send_reg_qr_code, name='event-send-reg-qr-code'),
    url(r'^event/(?P<id>\d+)/result/$', event_calendar_views.event_result, name='event-result'),
    url(r'^event/(?P<id>\d+)/dist/(?P<dist_id>\d+)/result/$', event_calendar_views.event_result, name='event-result-by-distance'),
    url(r'^event/(?P<id>\d+)/distance/update/$', event_calendar_views.reg_event_distance_update, name='reg-event-distance-update'), 
    url(r'^event/(?P<id>\d+)/result/uat/$', event_calendar_views.event_result_uat, name='event-result-uat'),
    url(r'^event/(?P<id>\d+)/checkpoint/result/$', event_calendar_views.checkpoint_result, name='event-result-checkpoint'),    
    url(r'^event/(?P<id>\d+)/checkpoint/result/(?P<dist_id>\d+)/distance/$', event_calendar_views.checkpoint_result_by_distance, name='event-result-checkpoint-distance'),
    url(r'^event/result/clear/$', event_calendar_views.result_clear, name='event-result-clear'),
    url(r'^event/result/normalize/$', event_calendar_views.result_date_normalize, name='result-date-normalize'),
    url(r'^event/(?P<id>\d+)/result/simple/$', event_calendar_views.event_result_simple, name='event-result-light'),
    url(r'^event/(?P<id>\d+)/result/(?P<point>\w+)/simple/$', event_calendar_views.event_result_simple, name='event-result-light-admin'), 
    url(r'^event/(?P<id>\d+)/result/(?P<point>\w+)/simple/offline/$', event_calendar_views.event_result_simple, {'full' : True}, name='event-result-light-admin-offline'),
    url(r'^rider/checkpoint/result/add/$', event_calendar_views.result_checkpoint_add, name='event-checkpoint-result-add'),
    url(r'^rider/checkpoint/result/add/package/$', event_calendar_views.result_checkpoint_add, name='event-checkpoint-result-add-package'),
    url(r'^event/checkpoint/result/clear/$', event_calendar_views.result_checkpoint_clear, name='event-checkpoint-result-clear'),    
    url(r'^rider/result/add/$', event_calendar_views.result_add, name='event-result-add'),
    url(r'^rider/result/add/chip/$', event_calendar_views.result_add_lviv, name='event-result-add-chip'),
    url(r'^rider/result/remove/$', event_calendar_views.result_remove, name='event-result-remove'),
    url(r'^event/registration/(?P<hash>[A-Fa-f0-9]{64})/$', event_calendar_views.register_to_all, name='other-event-registration'),
    url(r'^rider/start/edit/$', event_calendar_views.event_start, name='event-start'),
    url(r'^rider/(?P<id>\d+)/start/add/$', event_calendar_views.rider_start_add, name='rider-start-add'),
    url(r'^event/(?P<id>\d+)/registration/$', event_calendar_views.add_reg, name='event-registration'),
    url(r'^event/(?P<id>\d+)/registration/list/$', event_calendar_views.event_reg_list, name='event-rider-list'),
    url(r'^event/(?P<id>\d+)/registration/edit/number/$', event_calendar_views.event_reg_edit, name='event-rider-edit-number'),
    url(r'^event/(?P<id>\d+)/start/list/$', event_calendar_views.event_reg_list, {'start' : True}, name='event-start-list'),
    url(r'^event/(?P<id>\d+)/csv/$', event_calendar_views.csv_view, name='download-csv'),
    url(r'^event/(?P<id>\d+)/numbers/csv/$', event_calendar_views.csv_reg_list_view, name='download-csv-numbers'),
    url(r'^event/(?P<id>\d+)/result/uat/csv/$', event_calendar_views.csv_result_list_uat, name='download-csv-result'),
    url(r'^event/gps/get/$', event_calendar_views.get_event_gps),
    url(r'^event/rider/(?P<id>\d+)/info/$', event_calendar_views.get_event_rider, name='event-rider-info'),
    url(r'^event/rider/(?P<id>\d+)/pay/(?P<hash>[A-Fa-f0-9]{64})/$', event_calendar_views.add_rider_pay, name='rider-pay-submit'),
    url(r'^event/rider/(?P<id>\d+)/pay/$', event_calendar_views.add_rider_pay, name='rider-pay-submit-admin'),
    url(r'^event/rider/(?P<id>\d+)/registration/(?P<hash>[A-Fa-f0-9]{64})/edit/$', event_calendar_views.edit_reg, name='event-registration-edit'),
    url(r'^rider/registration/$', event_calendar_views.event_rider_status),
    url(r'^rider/(?P<id>\d+)/registration/copy/$', event_calendar_views.event_rider_copy, name='rider-reg-copy'),
    url(r'^rider/(?P<id>\d+)/registration/copy/(?P<evnt>\d+)/to/$', event_calendar_views.event_rider_copy, name='rider-reg-copy-to'),
    url(r'^rider/startstatus/$', event_calendar_views.rider_start_status),
    url(r'^rider/regstatus/$', event_calendar_views.rider_regstatus), # registration data
    url(r'^rider/(?P<id>\d+)/qrcode/app/$', event_calendar_views.rider_get_qr_app, name="rider-get-app-qrcode"), # get qr for insert data to app
    url(r'^event/(?P<id>\d+)/qrcode/app/$', event_calendar_views.event_qr_code_list, name="rider-list-get-app-qrcode"), # get qr for insert data to app
    url(r'^rider/(?P<id>\d+)/regstatus/$', event_calendar_views.rider_regstatus),
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
    url(r'^components/$', event_calendar_views.shop_company_list, name='components-company'),
    url(r'^components/type/list/$', event_calendar_views.shop_type_list, name='components-type-list'),
    url(r'^components/search/$', event_calendar_views.shop_search, name='components-search'),
    url(r'^components/sale/$', event_calendar_views.shop_components_sale, name='components-sale'),
    url(r'^components/new/delivery/$', event_calendar_views.shop_new_item, name='components-new-delivery'),
    url(r'^components/discount/$', event_calendar_views.shop_discount, name='components-discount'),
#    url(r'^blackfriday/$', event_calendar_views.shop_discount, name='components-discount'),
    url(r'^components/(?P<id>\d+)/brand/$', event_calendar_views.shop_components_brand, name='components-list-bybrand'),
    url(r'^components/(?P<id>\d+)/type/$', event_calendar_views.shop_components_type, name='components-list-bytype'),
    url(r'^components/(?P<id>\d+)/brand/sale/$', event_calendar_views.shop_components_brand_sale, name='components-list-bybrand-sale'),
    url(r'^components/(?P<id>\d+)/type/sale/$', event_calendar_views.shop_components_type_sale, name='components-list-bytype-sale'),

    url(r'^component/(?P<id>\d+)/$', event_calendar_views.shop_component, name='component-show'),
    url(r'^bicycles/$', event_calendar_views.shop_bicycle_company, name='bicycle-company'),
    url(r'^bicycles/kids/$', event_calendar_views.shop_bicycle_type),
    url(r'^bicycles/(?P<type>\d+)/type/$', event_calendar_views.shop_bicycle_type, name='bike-type-show'),
    url(r'^bicycles/(?P<id>\d+)/brand/$', event_calendar_views.shop_bicycle_brand, name='bicycle-list-bybrand'),
    url(r'^bicycles/(?P<id>\d+)/brand/sale/$', event_calendar_views.shop_bicycle_brand, {'sale': True}, name='bicycle-list-bybrand-sale'),
    url(r'^bicycles/(?P<id>\d+)/model/$', event_calendar_views.shop_bicycle, name='bicycle-show'),
#    url(r'^client/$', event_calendar_viewsshow_client'),
    url(r'^workshopshop/$', event_calendar_views.workshop_main, name='workshop-price'),
    url(r'^workshopshop/service/$', event_calendar_views.workshop_service, name='workshop-service'),
    url(r'^client/sale/$', event_calendar_views.client_sale),
    url(r'^client/(?P<user_name>[A-Za-z0-9_]+)/$', event_calendar_views.show_client, name='events_sale'),
    
    url(r'^routes/$', event_calendar_views.routes_list, name='routes'),
    url(r'^video/$', event_calendar_views.video_list, name='video'),
    
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