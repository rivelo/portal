# -*- coding: utf-8 -*-

from django.contrib import admin
from rivelo_portal.news.models import News, Category, Comments 


class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'text', 'date', 'link', 'author', 'category')
    list_filter = ('author', 'author')
    ordering = ('-date',)
    search_fields = ('title', 'text')

admin.site.register(News, NewsAdmin)

	
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'locality')
    ordering = ('name',)
    search_fields = ('name',)

admin.site.register(Category, CategoryAdmin)


class CommentsAdmin(admin.ModelAdmin):
    list_display = ('text', 'date', 'username')
    ordering = ('-date',)
    search_fields = ('text',)


admin.site.register(Comments, CommentsAdmin)















