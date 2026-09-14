import json
from datetime import timedelta

from django import template
from django.utils.safestring import mark_safe
from basiclive.utils.misc import natural_seconds
from basiclive.utils.functions import get_hours_per_shift

import numpy

register = template.Library()


@register.filter
def duration_shifts(td):
    return int(td.total_seconds() // 3600 / get_hours_per_shift())


@register.simple_tag
def filter_reports(sample, session=None):
    return sample.reports(session=session)


@register.simple_tag(takes_context=True)
def prep_messages(context):
    msgs = context.get('messages', [])
    output = []
    if msgs:
        output= [
            {
                'text': msg.message,
                'tags': msg.tags,
                'type': msg.level,
            }
            for msg in msgs
        ]
    return mark_safe(json.dumps(output))


@register.filter
def verbose_name(value):
    return value._meta.verbose_name


@register.filter
def get_item(d, key):
    return d


PLANCK = 4.13566733e-15  # eV.s
LIGHT_SPEED = 299792458e10    # A/s


@register.filter("energy_to_wavelength")
def energy_to_wavelength(energy):
    """Convert energy in keV to wavelength in angstroms."""
    energy = float(energy)
    if energy == 0.0:
        return 0.0
    return (PLANCK * LIGHT_SPEED)/(energy * 1000.0)


@register.filter("humanize_duration")
def humanize_duration(duration, sec=False):
    if isinstance(duration, (int, float)):
        return natural_seconds(timedelta(hours=duration).total_seconds())
    return natural_seconds(duration.total_seconds())


@register.filter("natural_duration")
def natural_duration(delta):
    return natural_seconds(delta.total_seconds())


class NumpyEncoder(json.JSONEncoder):
    """Custom encoder to convert NumPy types into standard Python types."""
    def default(self, obj):
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return super().default(obj)


@register.filter
def jsonify(data):
    return mark_safe(json.dumps(data, cls=NumpyEncoder))

