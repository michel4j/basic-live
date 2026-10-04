from django.contrib import admin
from basiclive.core.crm import models


class SupportRecordAdmin(admin.ModelAdmin):
    readonly_fields = ['previous']


admin.site.register(models.LikertScale)
admin.site.register(models.SupportArea)
admin.site.register(models.Feedback)
admin.site.register(models.SupportRecord, SupportRecordAdmin)
