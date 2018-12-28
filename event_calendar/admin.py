# -*- coding: utf-8 -*-

from django.contrib import admin
from portal.event_calendar.models import Events, EventType, Rules, GroupBikeType, BikeType, RegEvent, ResultEvent


class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('description', 'name' )
    ordering = ('name',)
    search_fields = ('name',)


class EventsAdmin(admin.ModelAdmin):
#    list_display = ('name', 'text', 'url', 'reg_url', 'photo', 'icon', 'forum_url', 'lat', 'lng', 'description', 'date', 'user', 'pub_date')
    ordering = ( '-pub_date', 'date',)
    search_fields = ('name', 'date')


class RulesAdmin(admin.ModelAdmin):
    pass


class GroupBikeTypeAdmin(admin.ModelAdmin):
    pass


class BikeTypeAdmin(admin.ModelAdmin):
    pass


class RegEventAdmin(admin.ModelAdmin):
    pass


class ResultEventAdmin(admin.ModelAdmin):
    pass


admin.site.register(BikeType, BikeTypeAdmin)
admin.site.register(GroupBikeType, GroupBikeTypeAdmin)
admin.site.register(EventType, EventTypeAdmin)
admin.site.register(Events, EventsAdmin)
admin.site.register(Rules, RulesAdmin)
admin.site.register(RegEvent, RegEventAdmin)
admin.site.register(ResultEvent, ResultEventAdmin)