from datetime import datetime

import msgpack
from django.contrib.auth import get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.html import escape


from basiclive.core.lims.conf import settings as lims_settings
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import edit, detail
from itemlist.views import ItemListView

from basiclive.utils import filters
from basiclive.utils.mixins import AsyncFormMixin, AdminRequiredMixin, PlotViewMixin, AuthenticationRequiredMixin
from . import models
from .forms import AccessForm
from basiclive.utils.network import get_client_address

User = get_user_model()


def format_beamlines(value, record):
    return ', '.join(record.beamline.values_list('acronym', flat=True))


def format_authorized_users(users, record):
    badges = []
    for user in users:
        if user.source == 'schedule':
            css_class = 'badge badge-success'
            title = 'Scheduled Access'
        else:
            css_class = 'badge badge-warning'
            title = 'Manual Access'
        badges.append(f'<span class="{css_class} badge-md" title="{title}">{escape(user.username.upper())}</span>')
    return ' '.join(badges)


class AccessListView(AdminRequiredMixin, ItemListView):
    model = models.AccessList
    list_filters = ['beamline']
    list_columns = ['name', 'description', 'annotated_users', 'address', 'beamlines']
    list_headers = {'annotated_users': 'Authorized Users'}
    list_transforms = {
        'beamlines': format_beamlines,
        'annotated_users': format_authorized_users,
    }
    list_search = ['name', 'description']
    tool_template = "acl/tools-access.html"
    link_url = 'access-edit'
    link_kwarg = 'address'
    link_attr = 'data-form-link'
    ordering = ['name']
    template_name = "lims/list.html"
    page_title = 'Access Endpoints'

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        return queryset.filter(active=True)


class AccessEdit(AdminRequiredMixin, SuccessMessageMixin, AsyncFormMixin, edit.UpdateView):
    form_class = AccessForm
    template_name = "lims/modal/form.html"
    model = models.AccessList
    success_url = reverse_lazy('access-list')
    success_message = "Access Control List has been updated."
    allowed_roles = ['owner', 'admin']
    admin_roles = ['admin']

    def get_object(self, queryset=None):
        return self.model.objects.get(address=self.kwargs.get('address'))


class AccessConnectionList(AdminRequiredMixin, ItemListView):
    model = models.Access
    list_columns = ['user', 'name', 'userlist', 'status', 'created', 'end']
    list_filters = ['created', filters.YearFilter('created', reverse=True), 'userlist', 'status']
    list_search = ['user__username', 'name', 'status', 'userlist__name', 'created']
    ordering = ['-created']
    template_name = "lims/list.html"
    link_url = 'access-connection-detail'
    link_attr = 'data-link'
    page_title = 'Access Connections'
    plot_url = reverse_lazy("connection-stats")
    paginate_by = 100


class AccessConnectionStats(PlotViewMixin, AccessConnectionList):
    plot_fields = {'user__kind__name': {}, 'userlist__name': {}, 'status': {}}
    date_field = 'created'
    list_url = reverse_lazy("access-connections")


class AccessConnectionDetail(AdminRequiredMixin, detail.DetailView):
    model = models.Access
    template_name = "acl/connection.html"


@method_decorator(csrf_exempt, name='dispatch')
class EndpointList(View):
    """
    Returns list of usernames that should be able to access the remote server referenced by the IP number inferred from
    the request.

    :key: r'^accesslist/$'
    """

    def get(self, request, *args, **kwargs):
        client_addr = get_client_address(request)

        userlist = models.AccessList.objects.filter(address=client_addr, active=True).first()

        if userlist:
            return JsonResponse(userlist.authorized_users(), safe=False)
        else:
            return JsonResponse([], safe=False)

    def post(self, request, *args, **kwargs):

        client_addr = get_client_address(request)
        user_list = models.AccessList.objects.filter(address=client_addr, active=True).first()

        errors = []

        if user_list:
            connections = msgpack.loads(request.body)
            for connection in connections:
                try:
                    project = models.Project.objects.get(username=connection['project'])
                except models.Project.DoesNotExist:
                    errors.append(f"User '{connection['project']}' not found.")
                status = connection['status']
                try:
                    event_time = datetime.strptime(connection['date'], "%Y-%m-%d %H:%M:%S")
                    dt = timezone.make_aware(event_time, timezone.get_current_timezone())
                    r, created = models.Access.objects.get_or_create(
                        name=connection['name'], userlist=user_list, user=project
                    )
                    r.status = status
                    if created:
                        r.created = dt
                    else:
                        r.end = dt
                    r.save()
                except Exception as e:
                    pass

            return JsonResponse(user_list.authorized_users(), safe=False)
        else:
            return JsonResponse([], safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class SSHKeys(View):
    """
    Returns SSH keys for specified user if the remote server referenced by the IP number inferred from
    the request exists.

    :key: r'^accesskeys/<username>$'
    """

    def get(self, request, *args, **kwargs):
        user = models.Project.objects.filter(username=self.kwargs.get('username')).first()

        msg = ''
        if user:
            msg = '\n'.join(user.sshkeys.values_list('key', flat=True)).encode()

        return HttpResponse(msg, content_type='text/plain')


@method_decorator(csrf_exempt, name='dispatch')
class AccessSSHKeys(AuthenticationRequiredMixin, View):
    """
    Returns SSH keys for the user if the remote server referenced by the IP number inferred from
    the request exists and the user is specifically allowed to access the host.

    :key: r'^keys/<username>$'
    """

    def get(self, request, *args, **kwargs):

        client_addr = get_client_address(request)
        user_list = models.AccessList.objects.filter(address=client_addr, active=True).first()
        user = models.Project.objects.filter(username=self.kwargs.get('username')).first()

        msg = ''
        if user and user_list and user.username in user_list.authorized_users():
            msg = '\n'.join(user.sshkeys.values_list('key', flat=True)).encode()

        return HttpResponse(msg, content_type='text/plain')
