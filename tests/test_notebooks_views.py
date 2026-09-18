import json
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import RequestFactory, TestCase, override_settings
from django.urls import include, path, reverse
from django.utils import timezone

from tests import setup_django

setup_django()

from basiclive.core.notebooks.models import (
    Entry,
    EntryType,
    Notebook,
    Theme,
)
from basiclive.core.notebooks import views

User = get_user_model()

urlpatterns = [
    path("notebooks/", include("basiclive.core.notebooks.urls")),
]


@override_settings(ROOT_URLCONF="tests.test_notebooks_views")
class NotebookViewsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        call_command('migrate', verbosity=0)
        super().setUpClass()

    def setUp(self):
        self.factory = RequestFactory()
        self.owner = User.objects.create_user(username="owner", password="password123", name="Owner")
        self.member = User.objects.create_user(username="member", password="password123", name="Member")
        self.other = User.objects.create_user(username="other", password="password123", name="Other")
        self.admin = User.objects.create_superuser(username="admin", password="password123", name="Admin")

        self.theme, _ = Theme.objects.get_or_create(name="default")
        self.text_type, _ = EntryType.objects.get_or_create(name="text", defaults={"description": "Text"})
        self.data_type, _ = EntryType.objects.get_or_create(name="data", defaults={"description": "Data"})

        # Notebooks with various access levels
        self.public_nb = Notebook.objects.create(
            name="public-nb",
            title="Public Notebook",
            description="Public Description",
            owner=self.owner,
            access=Notebook.ACCESS.public,
            editor=Notebook.EDITOR.owner,
        )

        self.internal_nb = Notebook.objects.create(
            name="internal-nb",
            title="Internal Notebook",
            description="Internal Description",
            owner=self.owner,
            access=Notebook.ACCESS.internal,
            editor=Notebook.EDITOR.team,
        )
        self.internal_nb.members.add(self.member)

        self.private_nb = Notebook.objects.create(
            name="private-nb",
            title="Private Notebook",
            description="Private Description",
            owner=self.owner,
            access=Notebook.ACCESS.private,
            editor=Notebook.EDITOR.team,
        )
        self.private_nb.members.add(self.member)

        self.other_private_nb = Notebook.objects.create(
            name="other-private-nb",
            title="Other Private Notebook",
            description="Other Private Description",
            owner=self.other,
            access=Notebook.ACCESS.private,
            editor=Notebook.EDITOR.owner,
        )

        # Create entries for testing
        self.now = timezone.now()
        self.today = timezone.localdate(self.now)
        self.yesterday = self.today - timedelta(days=1)
        self.yesterday_dt = self.now - timedelta(days=1)

        self.entry_yesterday = Entry.objects.create(
            notebook=self.private_nb,
            created=self.yesterday_dt,
            author=self.owner,
            text="Yesterday entry text",
            kind=self.text_type,
            tags=["sample", "protein"],
        )

        self.entry_today = Entry.objects.create(
            notebook=self.private_nb,
            created=self.now,
            author=self.owner,
            text="Today entry text",
            kind=self.text_type,
            tags=["buffer"],
        )

    def test_all_13_urls_reverse(self):
        """Verify all 13 URL endpoints reverse correctly."""
        self.assertEqual(reverse("notebooks:notebook-list"), "/notebooks/")
        self.assertEqual(reverse("notebooks:notebook-search"), "/notebooks/search/")
        self.assertEqual(reverse("notebooks:create-notebook"), "/notebooks/new/")
        self.assertEqual(reverse("notebooks:notebook-detail", kwargs={"pk": self.public_nb.pk}), f"/notebooks/{self.public_nb.pk}/")
        self.assertEqual(reverse("notebooks:notebook-edit", kwargs={"pk": self.public_nb.pk}), f"/notebooks/{self.public_nb.pk}/edit/")
        self.assertEqual(reverse("notebooks:create-entry", kwargs={"pk": self.public_nb.pk}), f"/notebooks/{self.public_nb.pk}/entry/")
        self.assertEqual(reverse("notebooks:delete-entry", kwargs={"pk": self.public_nb.pk}), f"/notebooks/{self.public_nb.pk}/remove/")
        self.assertEqual(reverse("notebooks:notebook-dates", kwargs={"pk": self.public_nb.pk}), f"/notebooks/{self.public_nb.pk}/dates/")
        self.assertEqual(reverse("notebooks:annotate-notebook", kwargs={"pk": self.public_nb.pk}), f"/notebooks/{self.public_nb.pk}/annotate/")
        self.assertEqual(reverse("notebooks:tag-notebook", kwargs={"pk": self.public_nb.pk}), f"/notebooks/{self.public_nb.pk}/tag/")
        self.assertEqual(reverse("notebooks:notebook-page", kwargs={"pk": self.entry_today.pk}), f"/notebooks/page/{self.entry_today.pk}/")
        self.assertEqual(reverse("notebooks:entry-data", kwargs={"pk": self.entry_today.pk}), f"/notebooks/entry/{self.entry_today.pk}/")
        self.assertEqual(reverse("notebooks:notebook-index", kwargs={"pk": self.entry_today.pk}), f"/notebooks/index/{self.entry_today.pk}/")

    def test_notebook_access_mixin_anonymous(self):
        """Anonymous user can only see public notebooks."""
        view = views.NotebookList()
        request = self.factory.get("/notebooks/")
        request.user = MagicMock(is_authenticated=False)
        view.request = request
        qs = view.get_queryset()
        self.assertIn(self.public_nb, qs)
        self.assertNotIn(self.internal_nb, qs)
        self.assertNotIn(self.private_nb, qs)
        self.assertNotIn(self.other_private_nb, qs)

    def test_notebook_access_mixin_authenticated_user(self):
        """Authenticated user sees public, internal, own private, and member private."""
        view = views.NotebookList()
        request = self.factory.get("/notebooks/")
        request.user = self.member
        view.request = request
        qs = view.get_queryset()
        self.assertIn(self.public_nb, qs)
        self.assertIn(self.internal_nb, qs)
        self.assertIn(self.private_nb, qs)  # member of private_nb
        self.assertNotIn(self.other_private_nb, qs)  # not member, not owner

    def test_notebook_access_mixin_superuser(self):
        """Superuser sees all notebooks."""
        view = views.NotebookList()
        request = self.factory.get("/notebooks/")
        request.user = self.admin
        view.request = request
        qs = view.get_queryset()
        self.assertEqual(set(qs), set(Notebook.objects.all()))

    def test_notebook_edit_mixin(self):
        """Test edit permissions on NotebookEditMixin."""
        view = views.UpdateNotebook()
        view.kwargs = {'pk': self.private_nb.pk}

        # Owner allowed
        request = self.factory.get(f"/notebooks/{self.private_nb.pk}/edit/")
        request.user = self.owner
        view.request = request
        self.assertTrue(view.test_func())

        # Superuser allowed
        request.user = self.admin
        view.request = request
        self.assertTrue(view.test_func())

        # Non-owner denied
        request.user = self.member
        view.request = request
        self.assertFalse(view.test_func())

    def test_notebook_list_context_data(self):
        """Verify NotebookList populates public, private, and internal buckets."""
        view = views.NotebookList()
        request = self.factory.get("/notebooks/")
        request.user = self.owner
        view.request = request
        view.object_list = view.get_queryset()
        context = view.get_context_data()
        self.assertIn('public', context['notebooks'])
        self.assertIn('private', context['notebooks'])
        self.assertIn('internal', context['notebooks'])
        self.assertIn(self.public_nb, context['notebooks']['public'])
        self.assertIn(self.private_nb, context['notebooks']['private'])

    def test_notebook_search_view(self):
        """Test NotebookSearch with different search tokens."""
        view = views.NotebookSearch()

        # Keyword in description/title
        request = self.factory.get("/notebooks/search/?q=Public")
        request.user = self.owner
        view.request = request
        view.object_list = view.get_queryset()
        context = view.get_context_data()
        self.assertIn(self.public_nb, context['notebooks'])

        # Search by tag
        request = self.factory.get("/notebooks/search/?q=tag:protein")
        request.user = self.owner
        view.request = request
        view.object_list = view.get_queryset()
        context = view.get_context_data()
        self.assertIn(self.entry_yesterday, context['entries'])

        # Search by author
        request = self.factory.get("/notebooks/search/?q=author:owner")
        request.user = self.owner
        view.request = request
        view.object_list = view.get_queryset()
        context = view.get_context_data()
        self.assertIn(self.entry_today, context['entries'])

        # Search with empty query
        request = self.factory.get("/notebooks/search/?q=")
        request.user = self.owner
        view.request = request
        view.object_list = view.get_queryset()
        context = view.get_context_data()
        self.assertEqual(len(context['notebooks']), 0)
        self.assertEqual(len(context['entries']), 0)

    def test_notebook_detail_view(self):
        """Test NotebookDetail context and entry ordering."""
        view = views.NotebookDetail()
        request = self.factory.get(f"/notebooks/{self.private_nb.pk}/")
        request.user = self.owner
        view.request = request
        view.object = self.private_nb
        context = view.get_context_data()
        self.assertEqual(len(context['entries']), 2)
        # Entries should be chronological
        self.assertEqual(context['entries'][0], self.entry_yesterday)
        self.assertEqual(context['entries'][1], self.entry_today)

    def test_notebook_dates_endpoint(self):
        """Test NotebookDates returns JSON list of page dates in given month."""
        self.client.force_login(self.owner)
        month_str = self.today.strftime("%Y%m")
        response = self.client.get(
            reverse("notebooks:notebook-dates", kwargs={"pk": self.private_nb.pk}),
            {"months": month_str},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(isinstance(data, list))
        dates = [d["date"] for d in data]
        self.assertIn(self.today.isoformat(), dates)

    def test_entry_data_endpoint(self):
        """Test EntryData JSON endpoint."""
        self.client.force_login(self.owner)
        response = self.client.get(
            reverse("notebooks:entry-data", kwargs={"pk": self.entry_today.pk})
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["text"], "Today entry text")

        # Non-member forbidden to access private entry data
        self.client.force_login(self.other)
        response = self.client.get(
            reverse("notebooks:entry-data", kwargs={"pk": self.entry_today.pk})
        )
        self.assertEqual(response.status_code, 403)

    @patch("basiclive.core.notebooks.views.loader.get_template")
    def test_notebook_page_endpoint(self, mock_get_template):
        """Test NotebookPage pagination view."""
        mock_template = MagicMock()
        mock_template.render.return_value = "<div>page</div>"
        mock_get_template.return_value = mock_template

        self.client.force_login(self.owner)
        # Load single entry anchor
        response = self.client.get(
            reverse("notebooks:notebook-page", kwargs={"pk": self.entry_today.pk})
        )
        self.assertEqual(response.status_code, 200)

        # Load prev entries
        response = self.client.get(
            reverse("notebooks:notebook-page", kwargs={"pk": self.entry_today.pk}),
            {"load": "prev"},
        )
        self.assertEqual(response.status_code, 200)

        # Load non-existent next page should return 204
        response = self.client.get(
            reverse("notebooks:notebook-page", kwargs={"pk": self.entry_today.pk}),
            {"load": "next"},
        )
        self.assertEqual(response.status_code, 204)

    @patch("basiclive.core.notebooks.views.loader.get_template")
    def test_notebook_index_endpoint(self, mock_get_template):
        """Test NotebookIndex view loads entries window."""
        mock_template = MagicMock()
        mock_template.render.return_value = "<div>index</div>"
        mock_get_template.return_value = mock_template

        self.client.force_login(self.owner)
        response = self.client.get(
            reverse("notebooks:notebook-index", kwargs={"pk": self.entry_today.pk}),
            {"load": 10, "active": self.entry_today.pk},
        )
        self.assertEqual(response.status_code, 200)

    @patch("basiclive.core.notebooks.views.loader.get_template")
    def test_save_entry_create_text(self, mock_get_template):
        """Test SaveEntry creates a new entry on current day."""
        mock_template = MagicMock()
        mock_template.render.return_value = "<div>new entry</div>"
        mock_get_template.return_value = mock_template

        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("notebooks:create-entry", kwargs={"pk": self.public_nb.pk}),
            {"text": "Brand new note", "kind": "text"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Entry.objects.filter(notebook=self.public_nb, text="Brand new note").exists()
        )

    @patch("basiclive.core.notebooks.views.loader.get_template")
    def test_save_entry_create_data_cleans_json(self, mock_get_template):
        """Test SaveEntry cleans JSON when kind is 'data'."""
        mock_template = MagicMock()
        mock_template.render.return_value = "<div>new data entry</div>"
        mock_get_template.return_value = mock_template

        raw_json = json.dumps({
            "headers": ["x", "y"],
            "data": {"0": [1.0, 2.0], "1": [3.14159265, 4.14159265]}
        })

        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("notebooks:create-entry", kwargs={"pk": self.public_nb.pk}),
            {"text": raw_json, "kind": "data"},
        )
        self.assertEqual(response.status_code, 200)
        entry = Entry.objects.filter(notebook=self.public_nb, kind=self.data_type).first()
        self.assertIsNotNone(entry)
        parsed = json.loads(entry.text)
        self.assertIn("headers", parsed)

    @patch("basiclive.core.notebooks.views.loader.get_template")
    def test_save_entry_update_existing(self, mock_get_template):
        """Test SaveEntry updates text of existing entry."""
        mock_template = MagicMock()
        mock_template.render.return_value = "<div>updated entry</div>"
        mock_get_template.return_value = mock_template

        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("notebooks:create-entry", kwargs={"pk": self.private_nb.pk}),
            {"pk": self.entry_today.pk, "text": "Updated entry content", "kind": "text"},
        )
        self.assertEqual(response.status_code, 200)
        self.entry_today.refresh_from_db()
        self.assertEqual(self.entry_today.text, "Updated entry content")

    @patch("basiclive.core.notebooks.views.loader.get_template")
    def test_save_entry_permission_denied(self, mock_get_template):
        """Non-editor cannot save entry."""
        self.client.force_login(self.other)
        response = self.client.post(
            reverse("notebooks:create-entry", kwargs={"pk": self.private_nb.pk}),
            {"text": "Unauthorized note", "kind": "text"},
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_entry_success(self):
        """Authorized user can delete today's entry."""
        # Create a dedicated notebook with a single entry for today
        del_nb = Notebook.objects.create(
            name="del-nb",
            title="Delete Notebook",
            owner=self.owner,
            access=Notebook.ACCESS.private,
            editor=Notebook.EDITOR.owner,
        )
        temp_entry = Entry.objects.create(
            notebook=del_nb,
            created=timezone.now(),
            author=self.owner,
            text="Delete me",
            kind=self.text_type,
        )

        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("notebooks:delete-entry", kwargs={"pk": del_nb.pk}),
            {"pk": temp_entry.pk},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Entry.objects.filter(pk=temp_entry.pk).exists())

    def test_delete_historical_entry_forbidden(self):
        """Historical entry from a previous day is immutable and cannot be deleted."""
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("notebooks:delete-entry", kwargs={"pk": self.private_nb.pk}),
            {"pk": self.entry_yesterday.pk},
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Entry.objects.filter(pk=self.entry_yesterday.pk).exists())

    def test_delete_entry_permission_denied(self):
        """Non-editor cannot delete entry."""
        self.client.force_login(self.other)
        response = self.client.post(
            reverse("notebooks:delete-entry", kwargs={"pk": self.private_nb.pk}),
            {"pk": self.entry_today.pk},
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Entry.objects.filter(pk=self.entry_today.pk).exists())

    @patch("basiclive.core.notebooks.views.loader.get_template")
    def test_annotate_entry_create_and_remove(self, mock_get_template):
        """Test AnnotateEntry create and remove methods."""
        mock_template = MagicMock()
        mock_template.render.return_value = "<div>annotated</div>"
        mock_get_template.return_value = mock_template

        self.client.force_login(self.owner)
        # Create annotation
        response = self.client.post(
            reverse("notebooks:annotate-notebook", kwargs={"pk": self.private_nb.pk}),
            {
                "entry_id": self.entry_today.pk,
                "method": "create",
                "kind": "highlight",
                "selection": "sel line 1\nsel line 2",
                "index": 1,
                "text": "Check this result",
            },
        )
        self.assertEqual(response.status_code, 200)
        annotation = self.entry_today.annotations.first()
        self.assertIsNotNone(annotation)
        self.assertEqual(annotation.text, "Check this result")
        self.assertEqual(annotation.selections, ["sel line 1", "sel line 2"])

        # Remove annotation
        response = self.client.post(
            reverse("notebooks:annotate-notebook", kwargs={"pk": self.private_nb.pk}),
            {
                "entry_id": self.entry_today.pk,
                "method": "remove",
                "pk": annotation.pk,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.entry_today.annotations.count(), 0)

    @patch("basiclive.core.notebooks.views.loader.get_template")
    def test_tag_entry(self, mock_get_template):
        """Test TagEntry sets tags on entry."""
        mock_template = MagicMock()
        mock_template.render.return_value = "<div>tagged</div>"
        mock_get_template.return_value = mock_template

        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("notebooks:tag-notebook", kwargs={"pk": self.private_nb.pk}),
            {
                "pk": self.entry_today.pk,
                "tags": "crystal, xray, diffraction",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.entry_today.refresh_from_db()
        self.assertEqual(set(self.entry_today.tags), {"crystal", "xray", "diffraction"})
