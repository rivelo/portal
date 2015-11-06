# -*- coding: utf-8 -*-

from django.contrib import admin
from rivelo_portal.funnies.models import Funnies


class FunniesAdmin(admin.ModelAdmin):
    list_display = ('text', 'rating', 'date', )
    ordering = ('text',)
    search_fields = ('text',)

admin.site.register(Funnies, FunniesAdmin)











