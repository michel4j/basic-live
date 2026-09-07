from datetime import datetime, timedelta
from django import template
from django.utils import timezone

register = template.Library()


def get_hours_per_shift() -> int:
    try:
        from basiclive.core.schedule.conf import settings as schedule_settings
        return schedule_settings.HOURS_PER_SHIFT
    except (ImportError, AttributeError):
        return 8


@register.simple_tag
def save_time(t):
    return t


@register.filter
def check_time(modified, last):
    if not last:
        return True
    return modified > (last + timedelta(minutes=15))


@register.filter
def duration_shifts(td):
    return int(td.total_seconds() // 3600 / get_hours_per_shift())