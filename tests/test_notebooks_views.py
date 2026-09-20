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

        self.text_type = EntryType.objects.filter(name__iexact="text").first() or EntryType.objects.create(name="text")
        self.data_type = EntryType.objects.filter(name__iexact="data").first() or EntryType.objects.create(name="data")

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

    def test_all_urls_reverse(self):
        """Verify all URL endpoints reverse correctly."""
        self.assertEqual(reverse("notebooks:notebook-list"), "/notebooks/")
        self.assertEqual(reverse("notebooks:create-notebook"), "/notebooks/new/")
        self.assertEqual(reverse("notebooks:notebook-detail", kwargs={"pk": self.public_nb.pk}), f"/notebooks/{self.public_nb.pk}/")
        self.assertEqual(reverse("notebooks:notebook-edit", kwargs={"pk": self.public_nb.pk}), f"/notebooks/{self.public_nb.pk}/edit/")
        self.assertEqual(reverse("notebooks:create-entry", kwargs={"book": self.public_nb.pk, "kind": "text"}), f"/notebooks/{self.public_nb.pk}/entry/new/text/")
        self.assertEqual(reverse("notebooks:edit-entry", kwargs={"book": self.public_nb.pk, "pk": self.entry_today.pk}), f"/notebooks/{self.public_nb.pk}/entry/{self.entry_today.pk}/edit/")
        self.assertEqual(reverse("notebooks:delete-entry", kwargs={"book": self.public_nb.pk, "pk": self.entry_today.pk}), f"/notebooks/{self.public_nb.pk}/entry/{self.entry_today.pk}/delete/")
        self.assertEqual(reverse("notebooks:notebook-dates", kwargs={"pk": self.public_nb.pk}), f"/notebooks/{self.public_nb.pk}/dates/")
        self.assertEqual(reverse("notebooks:annotate-notebook", kwargs={"pk": self.public_nb.pk}), f"/notebooks/{self.public_nb.pk}/annotate/")
        self.assertEqual(reverse("notebooks:tag-notebook", kwargs={"pk": self.public_nb.pk}), f"/notebooks/{self.public_nb.pk}/tag/")
        self.assertEqual(reverse("notebooks:entry-data", kwargs={"pk": self.entry_today.pk}), f"/notebooks/entry/{self.entry_today.pk}/")

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

    def test_notebook_dates_with_active_filters(self):
        """Test NotebookDates applies active list filters (tags, search, kind)."""
        self.client.force_login(self.owner)
        month_str = self.today.strftime("%Y%m")

        # Filter by tag 'protein' (only yesterday's entry has it)
        response = self.client.get(
            reverse("notebooks:notebook-dates", kwargs={"pk": self.private_nb.pk}),
            {"months": month_str, "tags": "protein"},
        )
        self.assertEqual(response.status_code, 200)
        dates = [d["date"] for d in response.json()]
        self.assertIn(self.yesterday.isoformat(), dates)
        self.assertNotIn(self.today.isoformat(), dates)

        # Filter by tag 'buffer' (only today's entry has it)
        response = self.client.get(
            reverse("notebooks:notebook-dates", kwargs={"pk": self.private_nb.pk}),
            {"months": month_str, "tags": "buffer"},
        )
        self.assertEqual(response.status_code, 200)
        dates = [d["date"] for d in response.json()]
        self.assertIn(self.today.isoformat(), dates)
        self.assertNotIn(self.yesterday.isoformat(), dates)

        # Search for text in today's entry using SEARCH_VAR ("search")
        response = self.client.get(
            reverse("notebooks:notebook-dates", kwargs={"pk": self.private_nb.pk}),
            {"months": month_str, "search": "Today"},
        )
        self.assertEqual(response.status_code, 200)
        dates = [d["date"] for d in response.json()]
        self.assertIn(self.today.isoformat(), dates)
        self.assertNotIn(self.yesterday.isoformat(), dates)

        # Search for text using 'q' query parameter
        response = self.client.get(
            reverse("notebooks:notebook-dates", kwargs={"pk": self.private_nb.pk}),
            {"months": month_str, "q": "Yesterday"},
        )
        self.assertEqual(response.status_code, 200)
        dates = [d["date"] for d in response.json()]
        self.assertIn(self.yesterday.isoformat(), dates)
        self.assertNotIn(self.today.isoformat(), dates)

        # Filter by kind (text)
        response = self.client.get(
            reverse("notebooks:notebook-dates", kwargs={"pk": self.private_nb.pk}),
            {"months": month_str, "kind__id__exact": self.text_type.pk},
        )
        self.assertEqual(response.status_code, 200)
        dates = [d["date"] for d in response.json()]
        self.assertIn(self.today.isoformat(), dates)
        self.assertIn(self.yesterday.isoformat(), dates)

        # Filter by kind with no entries (data)
        response = self.client.get(
            reverse("notebooks:notebook-dates", kwargs={"pk": self.private_nb.pk}),
            {"months": month_str, "kind__id__exact": self.data_type.pk},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

        # Filter by author (owner)
        response = self.client.get(
            reverse("notebooks:notebook-dates", kwargs={"pk": self.private_nb.pk}),
            {"months": month_str, "author__id__exact": self.owner.pk},
        )
        self.assertEqual(response.status_code, 200)
        dates = [d["date"] for d in response.json()]
        self.assertIn(self.today.isoformat(), dates)

        # Filter by author with no entries (member)
        response = self.client.get(
            reverse("notebooks:notebook-dates", kwargs={"pk": self.private_nb.pk}),
            {"months": month_str, "author__id__exact": self.member.pk},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_notebook_detail_date_filtering(self):
        """Test NotebookDetail date query parameter filtering and context."""
        self.client.force_login(self.owner)

        # Filter by today's date
        response = self.client.get(
            reverse("notebooks:notebook-detail", kwargs={"pk": self.private_nb.pk}),
            {"date": self.today.isoformat()},
        )
        self.assertEqual(response.status_code, 200)
        context = response.context_data
        entries = list(context["object_list"])
        self.assertIn(self.entry_today, entries)
        self.assertNotIn(self.entry_yesterday, entries)
        self.assertEqual(context["selected_date"], self.today.isoformat())
        self.assertEqual(context["latest_date"], self.today.isoformat())
        self.assertTrue(context["has_filters"])

        # Filter by yesterday's date
        response = self.client.get(
            reverse("notebooks:notebook-detail", kwargs={"pk": self.private_nb.pk}),
            {"date": self.yesterday.isoformat()},
        )
        self.assertEqual(response.status_code, 200)
        context = response.context_data
        entries = list(context["object_list"])
        self.assertNotIn(self.entry_today, entries)
        self.assertIn(self.entry_yesterday, entries)

    def test_notebook_detail_combined_filters(self):
        """Test NotebookDetail date filtering combined with kind, author, tags, and search."""
        # Create an entry on yesterday by member with data_type and distinct tag
        data_entry = Entry.objects.create(
            notebook=self.private_nb,
            created=self.yesterday_dt,
            author=self.member,
            text=json.dumps({"headers": ["Energy", "Counts"], "data": {"0": [100, 200], "1": [50, 75]}}),
            kind=self.data_type,
            tags=["spectrum"],
        )

        self.client.force_login(self.owner)

        # Filter date + kind (data)
        response = self.client.get(
            reverse("notebooks:notebook-detail", kwargs={"pk": self.private_nb.pk}),
            {"date": self.yesterday.isoformat(), "kind__id__exact": self.data_type.pk},
        )
        self.assertEqual(response.status_code, 200)
        entries = list(response.context_data["object_list"])
        self.assertEqual(entries, [data_entry])

        # Filter date + kind (text) on same date
        response = self.client.get(
            reverse("notebooks:notebook-detail", kwargs={"pk": self.private_nb.pk}),
            {"date": self.yesterday.isoformat(), "kind__id__exact": self.text_type.pk},
        )
        self.assertEqual(response.status_code, 200)
        entries = list(response.context_data["object_list"])
        self.assertEqual(entries, [self.entry_yesterday])

        # Filter date + author (member)
        response = self.client.get(
            reverse("notebooks:notebook-detail", kwargs={"pk": self.private_nb.pk}),
            {"date": self.yesterday.isoformat(), "author__id__exact": self.member.pk},
        )
        self.assertEqual(response.status_code, 200)
        entries = list(response.context_data["object_list"])
        self.assertEqual(entries, [data_entry])

        # Filter date + tag
        response = self.client.get(
            reverse("notebooks:notebook-detail", kwargs={"pk": self.private_nb.pk}),
            {"date": self.yesterday.isoformat(), "tags": "spectrum"},
        )
        self.assertEqual(response.status_code, 200)
        entries = list(response.context_data["object_list"])
        self.assertEqual(entries, [data_entry])

        # Filter date + search (via SEARCH_VAR 'search')
        response = self.client.get(
            reverse("notebooks:notebook-detail", kwargs={"pk": self.private_nb.pk}),
            {"date": self.yesterday.isoformat(), "search": "Energy"},
        )
        self.assertEqual(response.status_code, 200)
        entries = list(response.context_data["object_list"])
        self.assertEqual(entries, [data_entry])

        # Filter date + search (via 'q' parameter)
        response = self.client.get(
            reverse("notebooks:notebook-detail", kwargs={"pk": self.private_nb.pk}),
            {"date": self.yesterday.isoformat(), "q": "Energy"},
        )
        self.assertEqual(response.status_code, 200)
        entries = list(response.context_data["object_list"])
        self.assertEqual(entries, [data_entry])

    def test_notebook_detail_date_no_matches(self):
        """Test NotebookDetail with a date having no entries returns empty queryset."""
        self.client.force_login(self.owner)
        empty_date = "2000-01-01"
        response = self.client.get(
            reverse("notebooks:notebook-detail", kwargs={"pk": self.private_nb.pk}),
            {"date": empty_date},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context_data["object_list"]), [])
        self.assertEqual(response.context_data["selected_date"], empty_date)
        self.assertTrue(response.context_data["has_filters"])

    def test_notebook_detail_invalid_date(self):
        """Test NotebookDetail ignores invalid date query parameter gracefully."""
        self.client.force_login(self.owner)
        response = self.client.get(
            reverse("notebooks:notebook-detail", kwargs={"pk": self.private_nb.pk}),
            {"date": "not-a-valid-date"},
        )
        self.assertEqual(response.status_code, 200)
        context = response.context_data
        entries = list(context["object_list"])
        self.assertIn(self.entry_today, entries)
        self.assertIn(self.entry_yesterday, entries)

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

    def test_create_entry_modal_get(self):
        """GET request to CreateEntry renders modal form."""
        self.client.force_login(self.owner)
        response = self.client.get(
            reverse("notebooks:create-entry", kwargs={"book": self.public_nb.pk, "kind": "text"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Text Entry")

    def test_create_entry_modal_post_success(self):
        """POST request to CreateEntry creates new entry and returns JSON with redirect url."""
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("notebooks:create-entry", kwargs={"book": self.public_nb.pk, "kind": "text"}),
            {"text": "Brand new note", "tags": "log, run-1"},
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn("url", json_data)
        self.assertTrue(
            Entry.objects.filter(notebook=self.public_nb, text="Brand new note").exists()
        )
        entry = Entry.objects.get(notebook=self.public_nb, text="Brand new note")
        self.assertEqual(entry.author, self.owner)
        self.assertEqual(entry.tags, ["log", "run-1"])

    def test_create_entry_data_cleans_json(self):
        """POST request to CreateEntry with data kind cleans JSON payload."""
        raw_json = json.dumps({
            "headers": ["x", "y"],
            "data": {"0": [1.0, 2.0], "1": [3.14159265, 4.14159265]}
        })

        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("notebooks:create-entry", kwargs={"book": self.public_nb.pk, "kind": "data"}),
            {"text": raw_json, "tags": "data"},
        )
        self.assertEqual(response.status_code, 200)
        entry = Entry.objects.filter(notebook=self.public_nb, kind=self.data_type).first()
        self.assertIsNotNone(entry)
        parsed = json.loads(entry.text)
        self.assertIn("headers", parsed)

    def test_create_entry_permission_denied(self):
        """Non-editor cannot create entry."""
        self.client.force_login(self.other)
        response = self.client.post(
            reverse("notebooks:create-entry", kwargs={"book": self.private_nb.pk, "kind": "text"}),
            {"text": "Unauthorized note", "tags": ""},
        )
        self.assertEqual(response.status_code, 403)

    def test_update_entry_modal_get(self):
        """GET request to UpdateEntry renders modal form."""
        self.client.force_login(self.owner)
        response = self.client.get(
            reverse("notebooks:edit-entry", kwargs={"book": self.private_nb.pk, "pk": self.entry_today.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Text Entry")

    def test_update_entry_modal_post_success(self):
        """POST request to UpdateEntry updates entry content and returns JSON response."""
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("notebooks:edit-entry", kwargs={"book": self.private_nb.pk, "pk": self.entry_today.pk}),
            {"text": "Updated entry content", "tags": "updated, tag2"},
        )
        self.assertEqual(response.status_code, 200)
        self.entry_today.refresh_from_db()
        self.assertEqual(self.entry_today.text, "Updated entry content")
        self.assertEqual(self.entry_today.tags, ["updated", "tag2"])

    def test_update_entry_permission_denied(self):
        """Non-author cannot edit entry."""
        self.client.force_login(self.other)
        response = self.client.post(
            reverse("notebooks:edit-entry", kwargs={"book": self.private_nb.pk, "pk": self.entry_today.pk}),
            {"text": "Hijacked content", "tags": ""},
        )
        self.assertEqual(response.status_code, 403)

    def test_update_historical_entry_forbidden(self):
        """Historical entry from a previous day is immutable and cannot be updated."""
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("notebooks:edit-entry", kwargs={"book": self.private_nb.pk, "pk": self.entry_yesterday.pk}),
            {"text": "Trying to edit history", "tags": ""},
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_entry_success(self):
        """Authorized user can delete today's entry."""
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
            reverse("notebooks:delete-entry", kwargs={"book": del_nb.pk, "pk": temp_entry.pk}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Entry.objects.filter(pk=temp_entry.pk).exists())

    def test_delete_historical_entry_forbidden(self):
        """Historical entry from a previous day is immutable and cannot be deleted."""
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("notebooks:delete-entry", kwargs={"book": self.private_nb.pk, "pk": self.entry_yesterday.pk}),
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Entry.objects.filter(pk=self.entry_yesterday.pk).exists())

    def test_delete_entry_permission_denied(self):
        """Non-editor cannot delete entry."""
        self.client.force_login(self.other)
        response = self.client.post(
            reverse("notebooks:delete-entry", kwargs={"book": self.private_nb.pk, "pk": self.entry_today.pk}),
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
