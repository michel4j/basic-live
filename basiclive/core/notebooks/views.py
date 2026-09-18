import functools
import math
import operator
import re

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import Q
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotFound,
    JsonResponse,
)
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, View
from crisp_modals.views import ModalCreateView, ModalUpdateView

from .forms import NotebookForm
from .models import Annotation, Entry, EntryType, Notebook, Page
from .utils import clean_json, fuzzy_time


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
        context['notebooks'] = {
            'public': self.object_list.filter(access=self.model.ACCESS.public),
            'private': self.object_list.filter(access=self.model.ACCESS.private),
            'internal': self.object_list.filter(access=self.model.ACCESS.internal),
        }
        return context


class NotebookSearch(NotebookAccessMixin, ListView):
    model = Notebook
    template_name = "notebooks/notebook_search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_string = self.request.GET.get('q', '').strip()
        keywords = filter(None, [kw.strip() for kw in search_string.split(';')])
        query = Q()

        for keyword in keywords:
            if keyword.startswith('tag:'):
                query &= Q(tags__icontains=keyword[4:])
            elif keyword.startswith('author:'):
                query &= (Q(author__username=keyword[7:]) | Q(annotations__author__username=keyword[7:]))
            elif keyword.startswith('created:'):
                query &= fuzzy_time(keyword[8:], field='created')
            else:
                query &= (
                    Q(text__icontains=keyword)
                    | Q(annotations__text__icontains=keyword)
                )

        if search_string:
            context['notebooks'] = self.object_list.filter(
                Q(name__icontains=search_string)
                | Q(title__icontains=search_string)
                | Q(description__icontains=search_string)
            )[:10]
            context['entries'] = Entry.objects.filter(
                Q(page__book__in=self.object_list) & query
            ).distinct().order_by('-created')[:10]
        else:
            context['notebooks'] = self.model.objects.none()
            context['entries'] = Entry.objects.none()
        return context


class NotebookDetail(NotebookAccessMixin, DetailView):
    model = Notebook
    template_name = "notebooks/notebook.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = self.request.GET.get('date')
        if self.object.pages.exists():
            if date:
                pages = list(self.object.pages.filter(date__gte=date)[:2])
            else:
                pages = list(self.object.pages.order_by('-date')[:2])
                pages.reverse()
            context['pages'] = pages
            context['entries'] = Entry.objects.filter(page__in=pages)
        else:
            context['pages'] = []
            context['entries'] = Entry.objects.none()
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


class NotebookPage(View):
    model = Page
    template_name = "notebooks/pages.html"

    def get(self, request, *args, **kwargs):
        load = self.request.GET.get('load')
        try:
            obj = Page.objects.get(pk=self.kwargs.get('pk'))
        except Page.DoesNotExist:
            return HttpResponseNotFound("Page does not exist")

        if obj.book.can_view(self.request.user):
            if load:
                try:
                    if load == 'next':
                        pages = [obj.get_next_by_date(book=obj.book)]
                    elif load == 'prev':
                        pages = [obj.get_previous_by_date(book=obj.book)]
                    elif load == 'rest':
                        pages = list(obj.book.pages.filter(pk__gt=obj.pk))
                    else:
                        pages = [obj]
                except Page.DoesNotExist:
                    return HttpResponse(status=204)
            else:
                pages = [obj]
            t = loader.get_template(self.template_name)
            return HttpResponse(t.render({"pages": pages}, request))
        else:
            return HttpResponse(status=204)


class NotebookIndex(View):
    model = Entry
    template_name = "notebooks/index.html"

    def get(self, request, *args, **kwargs):
        num_load_val = self.request.GET.get('load')
        try:
            num_load = int(num_load_val) if num_load_val else 10
        except (ValueError, TypeError):
            num_load = 10
        active = self.request.GET.get('active')
        try:
            obj = Entry.objects.get(pk=self.kwargs.get('pk'))
        except Entry.DoesNotExist:
            return HttpResponseNotFound("Entry does not exist")

        if obj.page.book.can_view(self.request.user):
            entries = list(Entry.objects.filter(page__book=obj.page.book))
            load = math.ceil(num_load / 2)
            try:
                index = entries.index(obj)
            except ValueError:
                index = 0
            start_idx = max(0, index - load)
            end_idx = index + load
            loaded = entries[start_idx:end_idx]
            if len(loaded) < num_load:
                if index < load:
                    loaded = entries[:num_load]
                else:
                    loaded = entries[-num_load:] if len(entries) >= num_load else entries
            t = loader.get_template(self.template_name)
            ctx = {"entries": loaded}
            if active:
                try:
                    ctx["active"] = int(active)
                except (ValueError, TypeError):
                    pass
            return HttpResponse(t.render(ctx, request))
        else:
            return HttpResponse(status=204)


class SaveEntry(View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.POST
        try:
            book = Notebook.objects.get(id=self.kwargs.get('pk'))
        except Notebook.DoesNotExist:
            return HttpResponseNotFound("No notebook to write in")

        if not book.can_edit(request.user):
            return HttpResponseForbidden("Not allowed to edit notebook")

        text = data.get('text', '')
        kind_name = data.get('kind', 'text')
        try:
            kind = EntryType.objects.get(name=kind_name)
        except EntryType.DoesNotExist:
            kind = EntryType.objects.create(name=kind_name, description=kind_name.capitalize())

        if kind.name == 'data' and text:
            text = clean_json(text)
        author = request.user
        dt = timezone.localdate(timezone.now())

        if data.get('pk'):
            try:
                entry = Entry.objects.get(pk=data.get('pk'), page__book=book)
            except Entry.DoesNotExist:
                return HttpResponseNotFound("Entry not found")
            if not entry.can_edit(request.user):
                return HttpResponseForbidden("Not allowed to edit entry")
            entry.text = text
            entry.save()
            created_page = False
        else:
            page, created_page = Page.objects.get_or_create(book=book, date=dt)
            entry = Entry.objects.create(page=page, author=author, text=text, kind=kind)

        file_upload = request.FILES.get('file')
        if file_upload:
            entry.file.save(file_upload.name, file_upload)
            entry.save()

        if created_page:
            t = loader.get_template("notebooks/page.html")
        else:
            t = loader.get_template(f"notebooks/entries/{kind.name}.html")
        return HttpResponse(t.render({"entry": entry, "page": entry.page}, request))


class DeleteEntry(View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.POST
        try:
            book = Notebook.objects.get(id=self.kwargs.get('pk'))
            entry = Entry.objects.get(page__book=book, id=data.get('pk', 0))
        except (Notebook.DoesNotExist, Entry.DoesNotExist):
            return HttpResponseNotFound("Notebook entry not found!")

        if not (book.can_edit(request.user) and entry.can_edit(request.user)):
            return HttpResponseForbidden("Not allowed to delete entry!")

        page = entry.page
        entry.delete()
        if not page.entries.exists():
            page.delete()
        return HttpResponse("", status=200)


class AnnotateEntry(View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.POST
        try:
            book = Notebook.objects.get(id=self.kwargs.get('pk'))
            entry = Entry.objects.get(page__book=book, pk=data.get('entry_id', 0))
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

        t = loader.get_template(f"notebooks/entries/{entry.kind.name}.html")
        return HttpResponse(t.render({"entry": entry, "page": entry.page}, request))


class TagEntry(View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.POST
        try:
            book = Notebook.objects.get(id=self.kwargs.get('pk'))
            entry = Entry.objects.get(page__book=book, id=data.get('pk', 0))
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
        return HttpResponse(t.render({"entry": entry, "page": entry.page}, request))


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
        if month_list:
            query = functools.reduce(operator.or_, [
                Q(date__year=int(m[:4]), date__month=int(m[-2:])) for m in month_list
            ])
            pages_qs = notebook.pages.filter(query)
        else:
            pages_qs = notebook.pages.none()

        data = [
            {'date': page.date.isoformat(), 'title': '', 'location': ''}
            for page in pages_qs
        ]

        return JsonResponse(data, safe=False)
