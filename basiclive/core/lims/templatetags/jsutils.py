import json

import numpy
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


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

