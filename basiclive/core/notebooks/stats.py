"""Statistics and metrics reporting for basiclive.core.notebooks."""

from django.db.models import Count, Q

from .models import Annotation, Entry, EntryType, Notebook


def notebook_metrics(user=None):
    """
    Compute aggregate metrics for notebooks, entries, active days, and annotations.
    If user is specified, metrics are calculated for notebooks accessible by that user.
    """
    if user and not user.is_authenticated:
        notebook_qs = Notebook.objects.filter(access=Notebook.ACCESS.public)
    elif user and not user.is_superuser:
        notebook_qs = Notebook.objects.filter(
            Q(owner=user)
            | Q(access__gte=Notebook.ACCESS.internal)
            | Q(access=Notebook.ACCESS.private, members__pk=user.pk)
        ).distinct()
    else:
        notebook_qs = Notebook.objects.all()

    total_notebooks = notebook_qs.count()
    public_notebooks = notebook_qs.filter(access=Notebook.ACCESS.public).count()
    internal_notebooks = notebook_qs.filter(access=Notebook.ACCESS.internal).count()
    private_notebooks = notebook_qs.filter(access=Notebook.ACCESS.private).count()

    entries_qs = Entry.objects.filter(notebook__in=notebook_qs)
    total_entries = entries_qs.count()
    total_days = entries_qs.dates('created', 'day').count()

    annotations_qs = Annotation.objects.filter(entry__in=entries_qs)
    total_annotations = annotations_qs.count()

    kind_counts = dict(
        entries_qs.values_list('kind__name')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    return {
        'total_notebooks': total_notebooks,
        'public_notebooks': public_notebooks,
        'internal_notebooks': internal_notebooks,
        'private_notebooks': private_notebooks,
        'total_days': total_days,
        'total_entries': total_entries,
        'total_annotations': total_annotations,
        'entries_by_kind': kind_counts,
    }


def project_notebook_metrics(project):
    """
    Compute notebook metrics scoped to a specific project or owner.
    """
    notebook_qs = Notebook.objects.filter(Q(owner=project) | Q(project=project)).distinct()
    entries_qs = Entry.objects.filter(notebook__in=notebook_qs)
    total_days = entries_qs.dates('created', 'day').count()

    return {
        'total_notebooks': notebook_qs.count(),
        'total_days': total_days,
        'total_entries': entries_qs.count(),
        'entries_by_kind': dict(
            entries_qs.values_list('kind__name')
            .annotate(total=Count('id'))
            .order_by('-total')
        ),
    }
