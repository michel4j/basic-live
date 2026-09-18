from django.contrib import admin

from . import models


@admin.register(models.Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(models.EntryType)
class EntryTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(models.Notebook)
class NotebookAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'owner', 'access', 'editor', 'created', 'modified')
    list_filter = ('access', 'editor')
    search_fields = ('title', 'name', 'description', 'owner__username', 'owner__name')


@admin.register(models.Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('notebook', 'author', 'kind', 'created')
    list_filter = ('kind', 'created')
    search_fields = ('text', 'tags', 'author__username', 'notebook__title', 'notebook__name')


@admin.register(models.Annotation)
class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('entry', 'author', 'kind', 'created')
    list_filter = ('kind', 'created')
    search_fields = ('text', 'author__username')
