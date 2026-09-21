import datetime
import functools
import operator
import re
from typing import Any

from crisp_modals.views import ModalCreateView, ModalUpdateView, ModalDeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import Q
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotFound,
    JsonResponse, )
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, View
from itemlist.views import ItemListView, SEARCH_VAR

from .forms import NotebookForm, get_entry_form_class, TagsForm
from .models import Entry, EntryType, Notebook
from ...utils.filters import TagFilter


class NotebookAccessMixin:
    """Restricts queryset based on notebook access and user authentication."""
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user.is_authenticated:
            return qs.filter(access=Notebook.ACCESS.public)
        if user.is_superuser:
            return qs
        return qs.filter(
            Q(owner=user)
            | Q(access__gte=Notebook.ACCESS.internal)
            | Q(access=Notebook.ACCESS.private, members__pk=user.pk)
        ).distinct()


class NotebookEditMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restricts editing to notebook owners and superusers."""
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        try:
            obj = self.get_object()
        except (Http404, self.model.DoesNotExist):
            return False
        return obj.owner == user

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return super().get_queryset().none()
        if user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(owner=user)


class NotebookList(NotebookAccessMixin, ListView):
    model = Notebook
    template_name = "notebooks/notebook_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notebooks'] = self.object_list
        return context


class NotebookDetail(LoginRequiredMixin, ItemListView):
    model = Entry
    paginate_by = 5
    list_filters = ['kind', 'author', TagFilter('tags')]
    list_search = ['author__username', 'tags', 'text', 'annotations__text', 'annotations__author__username']
    list_ordering = ['-created']
    template_name = "notebooks/notebook.html"

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)
        user = self.request.user
        flt = Q(notebook__pk=self.kwargs.get('pk'))
        if not (user.is_authenticated and user.is_superuser):
            flt &= (
                Q(notebook__owner=user)
                | Q(notebook__access__gte=Notebook.ACCESS.internal)
                | Q(notebook__access=Notebook.ACCESS.private, notebook__members=user)
            )
        date_str = self.request.GET.get('date', '').strip() or self.kwargs.get('date')
        if date_str:
            try:
                date_obj = datetime.date.fromisoformat(date_str)
                flt &= Q(created__date=date_obj)
                self.has_filters = True
            except (ValueError, TypeError):
                pass

        q_search = self.request.GET.get('q', '').strip()
        if q_search and SEARCH_VAR not in self.request.GET:
            qs, _ = self.get_search_results(qs, q_search)
            self.has_filters = True

        return qs.filter(flt).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            notebook = Notebook.objects.get(pk=self.kwargs.get('pk'))
        except Notebook.DoesNotExist:
            raise Http404("Notebook does not exist")

        if not notebook.can_view(self.request.user):
            raise Http404("Notebook does not exist")

        context['notebook'] = notebook
        context['can_edit'] = notebook.can_edit(self.request.user)
        context['selected_date'] = self.request.GET.get('date', '').strip()
        latest_entry = notebook.entries.order_by('-created').first()
        if latest_entry:
            context['latest_date'] = timezone.localdate(latest_entry.created).isoformat()
        else:
            context['latest_date'] = timezone.localdate(timezone.now()).isoformat()
        context['has_filters'] = self.has_filters
        return context


class CreateNotebook(LoginRequiredMixin, SuccessMessageMixin, ModalCreateView):
    model = Notebook
    form_class = NotebookForm
    success_message = _("Notebook has been created.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('notebooks:notebook-detail', kwargs={'pk': self.object.pk})


class UpdateNotebook(NotebookEditMixin, SuccessMessageMixin, ModalUpdateView):
    model = Notebook
    form_class = NotebookForm
    success_message = _("Notebook has been updated.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('notebooks:notebook-detail', kwargs={'pk': self.object.pk})


class CreateEntry(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, ModalCreateView):
    model = Entry
    success_message = _("Entry has been created.")
    size = 'lg'

    def get_notebook(self):
        if not hasattr(self, '_notebook'):
            book_id = self.kwargs.get('book') or self.kwargs.get('pk')
            self._notebook = Notebook.objects.get(pk=book_id)
        return self._notebook

    def get_entry_type(self):
        if not hasattr(self, '_entry_type'):
            kind_str = self.kwargs.get('kind', 'text')
            entry_type = EntryType.objects.filter(name__iexact=kind_str).first()
            if not entry_type:
                entry_type = EntryType.objects.create(name=kind_str.title())
            self._entry_type = entry_type
        return self._entry_type

    def get_form_class(self):
        entry_type = self.get_entry_type()
        form_class = get_entry_form_class(entry_type)
        if not form_class:
            raise Http404(f"Unknown entry kind: {entry_type.name}")
        return form_class

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['notebook'] = self.get_notebook()
        kwargs['kind'] = self.get_entry_type()
        return kwargs

    def form_valid(self, form):
        form.instance.notebook = self.get_notebook()
        form.instance.author = self.request.user
        form.instance.kind = self.get_entry_type()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('notebooks:notebook-detail', kwargs={'pk': self.get_notebook().pk})

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        try:
            notebook = self.get_notebook()
        except (Notebook.DoesNotExist, ValueError):
            return False
        return notebook.can_edit(user)


class UpdateEntry(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, ModalUpdateView):
    model = Entry
    success_message = _("Entry has been updated.")
    size = 'lg'

    def get_form_class(self):
        form_class = get_entry_form_class(self.object.kind)
        if not form_class:
            raise Http404(f"Unknown entry kind: {self.object.kind.name}")
        return form_class

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['notebook'] = self.object.notebook
        kwargs['kind'] = self.object.kind
        return kwargs

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        initial['tags'] = ';'.join(self.object.tags or [])
        return initial

    def get_success_url(self):
        return reverse('notebooks:notebook-detail', kwargs={'pk': self.object.notebook.pk})

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        try:
            entry = self.get_object()
        except (Http404, self.model.DoesNotExist):
            return False
        book_id = self.kwargs.get('book')
        if book_id and str(entry.notebook.pk) != str(book_id):
            return False
        return entry.can_edit(user)


class EditTags(UpdateEntry):
    form_class = TagsForm
    size = 'md'

    def get_form_class(self):
        return TagsForm


class DeleteEntry(LoginRequiredMixin, UserPassesTestMixin, ModalDeleteView):
    model = Entry

    def get_success_url(self):
        book = self.object.notebook
        return reverse('notebooks:notebook-detail', kwargs={'pk': book.pk})

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        try:
            entry = self.get_object()
        except (Http404, self.model.DoesNotExist):
            return False
        return entry.notebook.can_edit(user) and entry.can_edit(user)


class AnnotateEntry(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        try:
            book = Notebook.objects.get(id=self.kwargs.get('book'))
            entry = Entry.objects.get(notebook=book, pk=self.kwargs.get('pk'))
        except (Http404, Notebook.DoesNotExist, Entry.DoesNotExist):
            return False
        return entry.notebook.can_view(user)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.POST
        try:
            book = Notebook.objects.get(id=self.kwargs.get('book'))
            entry = Entry.objects.get(notebook=book, pk=self.kwargs.get('pk'))
        except (Notebook.DoesNotExist, Entry.DoesNotExist):
            return HttpResponseNotFound("Notebook entry not found!")

        if not book.can_edit(request.user):
            return HttpResponseForbidden("Operation not allowed!")

        method = data.get('method')
        if method == 'create':
            selection_raw = data.get('selection', '')
            selections = selection_raw.split('\n') if selection_raw else []
            entry.annotations.create(
                kind=data.get('kind', 'note'),
                selections=selections,
                node_index=data.get('index', 0),
                text=data.get('text', ''),
                author=request.user,
            )
        elif method == 'remove' and data.get('pk'):
            entry.annotations.filter(pk=data['pk'], author=request.user).delete()
        return JsonResponse({"status": "ok"})


class TagEntry(View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.POST
        try:
            book = Notebook.objects.get(id=self.kwargs.get('pk'))
            entry = Entry.objects.get(notebook=book, id=data.get('pk', 0))
        except (Notebook.DoesNotExist, Entry.DoesNotExist):
            return HttpResponseNotFound("Notebook entry not found!")

        if not book.can_edit(request.user):
            return HttpResponseForbidden("Operation not allowed!")

        raw_tags = data.get('tags', '')
        new_tags = set(filter(None, [t.strip() for t in re.split(r'[,;]', raw_tags)]))
        if entry.can_edit(request.user):
            entry.tags = list(new_tags)
        else:
            entry.tags = list(set(entry.tags or []) | new_tags)
        entry.save()

        t = loader.get_template(f"notebooks/entries/{entry.kind.name}.html")
        return HttpResponse(t.render({"entry": entry, "notebook": book}, request))


class EntryData(DetailView):
    model = Entry

    def get(self, request, *args, **kwargs):
        try:
            obj = self.get_object(self.get_queryset())
        except (self.model.DoesNotExist, Http404):
            return HttpResponseNotFound("Entry not found!")

        if not obj.can_view(request.user):
            return HttpResponseForbidden("Not allowed to view entry!")

        data = {
            'text': obj.text,
            'file': {'url': obj.file.url, 'mime': obj.mimetype()} if obj.file else "",
        }
        return JsonResponse(data)


class NotebookDates(NotebookAccessMixin, DetailView):
    model = Notebook

    def get(self, request, *args, **kwargs):
        try:
            notebook = self.get_object(self.get_queryset())
        except (self.model.DoesNotExist, Http404):
            return JsonResponse([], safe=False)

        date = timezone.localdate(timezone.now())
        months = request.GET.get('months', date.strftime('%Y%m'))
        month_list = [m.strip() for m in months.split(',') if len(m.strip()) == 6]
        if not month_list:
            return JsonResponse([], safe=False)

        query = functools.reduce(operator.or_, [
            Q(created__year=int(m[:4]), created__month=int(m[-2:])) for m in month_list
        ])
        entries = notebook.entries.filter(query)

        # Apply active list filters from NotebookDetail (kind, author, tags, search)
        detail_view = NotebookDetail()
        detail_view.request = request
        detail_view.kwargs = {'pk': notebook.pk}
        detail_view.model = Entry

        filter_specs, _, _ = detail_view.get_filters()
        for filter_spec in filter_specs:
            new_entries = filter_spec.queryset(request, entries)
            entries = new_entries if new_entries is not None else entries

        search_text = request.GET.get(SEARCH_VAR, '') or request.GET.get('q', '')
        if search_text:
            entries, _ = detail_view.get_search_results(entries, search_text)

        dates_qs = entries.dates('created', 'day')
        data = [
            {'date': d.isoformat(), 'title': '', 'location': ''}
            for d in dates_qs
        ]

        return JsonResponse(data, safe=False)
