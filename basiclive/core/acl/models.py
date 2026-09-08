import os
from datetime import timedelta
from typing import NamedTuple

from django.db import models
from django.utils import timezone
from model_utils import Choices

from basiclive.core.lims.conf import settings as lims_settings


class AnnotatedUser(NamedTuple):
    username: str
    source: str


def get_hours_per_shift() -> int:
    try:
        from basiclive.core.schedule.conf import settings as schedule_settings
        return schedule_settings.HOURS_PER_SHIFT
    except (ImportError, AttributeError):
        return 8


if lims_settings.USE_SCHEDULE:
    from basiclive.core.schedule.models import Beamtime


def get_storage_path(instance, filename):
    return os.path.join('uploads/', 'links', filename)


class AccessList(models.Model):
    name = models.CharField(max_length=60, unique=True)
    description = models.TextField(blank=True, null=True)
    address = models.GenericIPAddressField()
    users = models.ManyToManyField("lims.Project", blank=True)
    active = models.BooleanField(default=False)
    created = models.DateTimeField('date created', auto_now_add=True, editable=False)
    modified = models.DateTimeField('date modified', auto_now_add=True, editable=False)
    beamline = models.ManyToManyField("lims.Beamline", blank=True, related_name="access_lists")

    def authorized_users(self):
        return [u.username for u in self.annotated_users()]

    def scheduled(self):
        if lims_settings.USE_SCHEDULE:
            now = timezone.localtime()
            slot = get_hours_per_shift()
            user_names = Beamtime.objects.filter(
                cancelled=False,
                access__remote=True,
                beamline__in=self.beamline.all(),
                start__lte=now,
                end__gte=now - timedelta(hours=int(slot / 2))
            ).values_list(
                'project__username',
                flat=True
            ).order_by().distinct()
            return list(user_names)
        return []

    def annotated_users(self) -> list[AnnotatedUser]:
        if lims_settings.USE_SCHEDULE:
            scheduled_set = set(self.scheduled())
        else:
            scheduled_set = set()
        manual_set = set(self.users.values_list('username', flat=True)) - scheduled_set

        scheduled_users = [AnnotatedUser(u, 'schedule') for u in sorted(scheduled_set)]
        manual_users = [AnnotatedUser(u, 'manual') for u in sorted(manual_set)]
        return scheduled_users + manual_users

    def identity(self):
        return self.name

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "Access List"


class Access(models.Model):
    STATES = Choices(
        ('CONNECTED', 'Connected'),
        ('DISCONNECTED', 'Disconnected'),
        ('FAILED', 'Failed'),
        ('FINISHED', 'Finished'),
    )
    name = models.CharField(max_length=48)
    user = models.ForeignKey("lims.Project", on_delete=models.CASCADE)
    userlist = models.ForeignKey(AccessList, related_name="connections", on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    created = models.DateTimeField('date created', auto_now_add=True, editable=True)
    end = models.DateTimeField('date ended', null=True, blank=True)

    def is_active(self):
        return self.status in ['Connected', 'Disconnected']

    def total_time(self):
        end = self.end or timezone.now()
        return (end - self.created).total_seconds()/3600.
    total_time.short_description = "Duration"
