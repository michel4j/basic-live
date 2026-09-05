from importlib.metadata import version


def version_context_processor(request):
    """
    Version context processor
    """
    return {'version': version('basic-live')}

