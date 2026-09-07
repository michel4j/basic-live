from django import template
from django.conf import settings as django_settings

from basiclive.core.lims.conf import settings as lims_settings

register = template.Library()


@register.simple_tag
def get_setting(key, default=""):
    normalized_key = key.removeprefix("LIMS_") if key.startswith("LIMS_") else key
    if normalized_key in lims_settings:
        return getattr(lims_settings, normalized_key)
    return getattr(django_settings, key, default)


@register.simple_tag
def get_setting(key, default=""):
    normalized_key = key.removeprefix("LIMS_") if key.startswith("LIMS_") else key
    if normalized_key in lims_settings:
        return getattr(lims_settings, normalized_key)
    return getattr(django_settings, key, default)