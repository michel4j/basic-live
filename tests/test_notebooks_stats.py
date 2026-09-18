import unittest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.utils import timezone

from django.core.management import call_command
from tests import setup_django
setup_django()

from basiclive.core.notebooks.models import (
    Annotation,
    Entry,
    EntryType,
    Notebook,
)
from basiclive.core.notebooks import stats


class NotebooksStatsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        call_command('migrate', verbosity=0)
        super().setUpClass()

    def setUp(self):
        User = get_user_model()
        self.superuser = User.objects.create_superuser(
            username="admin", password="password", email="admin@example.com"
        )
        self.user1 = User.objects.create_user(
            username="user1", password="password", email="user1@example.com"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="password", email="user2@example.com"
        )

        self.text_type, _ = EntryType.objects.get_or_create(name="text")
        self.data_type, _ = EntryType.objects.get_or_create(name="data")

        # Create public notebook
        self.nb_pub = Notebook.objects.create(
            name="pub-book",
            title="Public Book",
            owner=self.user1,
            access=Notebook.ACCESS.public,
        )
        # Create internal notebook
        self.nb_int = Notebook.objects.create(
            name="int-book",
            title="Internal Book",
            owner=self.user1,
            access=Notebook.ACCESS.internal,
        )
        # Create private notebook owned by user1, shared with user2
        self.nb_priv = Notebook.objects.create(
            name="priv-book",
            title="Private Book",
            owner=self.user1,
            access=Notebook.ACCESS.private,
        )
        self.nb_priv.members.add(self.user2)

        # Create private notebook owned by user2, not shared
        self.nb_priv2 = Notebook.objects.create(
            name="priv2-book",
            title="Private Book 2",
            owner=self.user2,
            access=Notebook.ACCESS.private,
        )

        # Entries
        self.entry1 = Entry.objects.create(
            notebook=self.nb_pub,
            kind=self.text_type,
            author=self.user1,
            text="Note 1",
        )
        self.entry2 = Entry.objects.create(
            notebook=self.nb_pub,
            kind=self.data_type,
            author=self.user1,
            text='{"title": "Data 1"}',
        )

        self.annotation = Annotation.objects.create(
            entry=self.entry1,
            author=self.user2,
            text="Great note",
        )

    def test_notebook_metrics_all(self):
        """Verify metrics without user filter computes totals across all notebooks."""
        metrics = stats.notebook_metrics()
        self.assertEqual(metrics["total_notebooks"], 4)
        self.assertEqual(metrics["public_notebooks"], 1)
        self.assertEqual(metrics["internal_notebooks"], 1)
        self.assertEqual(metrics["private_notebooks"], 2)
        self.assertEqual(metrics["total_days"], 1)
        self.assertEqual(metrics["total_entries"], 2)
        self.assertEqual(metrics["total_annotations"], 1)
        self.assertEqual(metrics["entries_by_kind"], {"text": 1, "data": 1})

    def test_notebook_metrics_superuser(self):
        """Verify superuser sees all notebooks."""
        metrics = stats.notebook_metrics(user=self.superuser)
        self.assertEqual(metrics["total_notebooks"], 4)

    def test_notebook_metrics_anonymous_user(self):
        """Verify anonymous user sees only public notebooks."""
        anon = AnonymousUser()
        metrics = stats.notebook_metrics(user=anon)
        self.assertEqual(metrics["total_notebooks"], 1)
        self.assertEqual(metrics["public_notebooks"], 1)
        self.assertEqual(metrics["internal_notebooks"], 0)
        self.assertEqual(metrics["private_notebooks"], 0)

    def test_notebook_metrics_authenticated_user(self):
        """Verify normal authenticated user sees public, internal, and their own/shared private notebooks."""
        metrics = stats.notebook_metrics(user=self.user2)
        # user2 should see: pub (public), int (internal), priv (member), priv2 (owner) = 4
        self.assertEqual(metrics["total_notebooks"], 4)

        # Create another private notebook not owned by or shared with user2
        User = get_user_model()
        user3 = User.objects.create_user(username="user3", password="password")
        Notebook.objects.create(
            name="priv3-book",
            title="Private Book 3",
            owner=user3,
            access=Notebook.ACCESS.private,
        )
        metrics2 = stats.notebook_metrics(user=self.user2)
        self.assertEqual(metrics2["total_notebooks"], 4)

    def test_project_notebook_metrics(self):
        """Verify project_notebook_metrics filters notebooks correctly."""
        metrics1 = stats.project_notebook_metrics(self.user1)
        self.assertEqual(metrics1["total_notebooks"], 3)
        self.assertEqual(metrics1["total_days"], 1)
        self.assertEqual(metrics1["total_entries"], 2)
        self.assertEqual(metrics1["entries_by_kind"], {"text": 1, "data": 1})

        metrics2 = stats.project_notebook_metrics(self.user2)
        self.assertEqual(metrics2["total_notebooks"], 1)
        self.assertEqual(metrics2["total_days"], 0)
        self.assertEqual(metrics2["total_entries"], 0)
        self.assertEqual(metrics2["entries_by_kind"], {})


if __name__ == "__main__":
    unittest.main()
