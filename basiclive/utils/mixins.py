from urllib import parse

from django import http
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from ..utils.stats import generic_stats

TEMP_PREFIX = getattr(settings, 'PDF_TEMP_PREFIX', 'render_pdf-')
CACHE_PREFIX = getattr(settings, 'PDF_CACHE_PREFIX', 'render-pdf')
CACHE_TIMEOUT = getattr(settings, 'PDF_CACHE_TIMEOUT', 30)  # 86400)  # 1 day


def is_ajax(request: HttpRequest) -> bool:
    """
    https://stackoverflow.com/questions/63629935
    """
    return (
        request.headers.get('x-requested-with') == 'XMLHttpRequest'
        or request.accepts("application/json")
    )


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin to allow access through a view only if the user is a superuser.
    Can be used with any View.
    """
    def test_func(self):
        return self.request.user.is_superuser


@method_decorator(csrf_exempt, name='dispatch')
class AuthenticationRequiredMixin(object):
    """
    Mixin to verify that the user is logged-in without any redirects
    """

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request, 'user') and request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        else:
            return http.HttpResponseForbidden()


class AsyncFormMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    modal_response = False

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super().form_valid(form)
        if is_ajax(self.request):
            data = {
                'modal': self.modal_response,
                'url': self.get_success_url(),
            }
            return JsonResponse(data, safe=False)
        else:
            return response


class PlotViewMixin:
    template_name = "lims/list-plots.html"
    plot_fields = []
    date_field = None
    paginate_by = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report'] = self.get_metrics()
        context['active_filters'] = self.get_active_filters()
        return context

    def get_plot_fields(self):
        return self.plot_fields

    def get_active_filters(self):
        qsl = self.get_query_string()
        if self.date_field:
            for part in ['year', 'month', 'day', 'quarter']:
                qsl = qsl.replace('{}_{}'.format(self.date_field, part), '{}__{}'.format(self.date_field, part))
        return dict(parse.parse_qsl(qsl.strip('?')))

    def get_metrics(self):
        return generic_stats(self.get_queryset(), self.get_plot_fields(), self.date_field)
