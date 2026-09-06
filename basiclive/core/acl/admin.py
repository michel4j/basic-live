from django.contrib import admin

from .models import AccessList


class AccessListAdmin(admin.ModelAdmin):
    search_fields = ['name', 'description', 'address']
    list_filter = ['created', 'modified', 'active']
    list_display = ['id', 'name', 'address', 'description', 'active', 'modified']
    ordering = ['-created']


admin.site.register(AccessList, AccessListAdmin)
