import json
import unittest
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from tests import setup_django

setup_django()

from basiclive.core.notebooks.models import (
    Annotation,
    Entry,
    EntryType,
    Notebook,
    Page,
    Theme,
)
from basiclive.core.notebooks.fields import StringListField, DelimitedTextFormField
from basiclive.core.notebooks.utils import (
    clean_json,
    fuzzy_time,
    simpletime,
    timeish,
)

User = get_user_model()


class NotebookModelsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        call_command('migrate', verbosity=0)
        super().setUpClass()

    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="password123", name="Owner")
        self.member = User.objects.create_user(username="member", password="password123", name="Member")
        self.other = User.objects.create_user(username="other", password="password123", name="Other")
        self.admin = User.objects.create_superuser(username="admin", password="password123", name="Admin")

        self.theme, _ = Theme.objects.get_or_create(name="default")
        self.entry_type_text, _ = EntryType.objects.get_or_create(name="text")
        self.entry_type_data, _ = EntryType.objects.get_or_create(name="data")

        self.notebook = Notebook.objects.create(
            name="test-notebook",
            title="Test Notebook",
            description="A test notebook description",
            owner=self.owner,
            access=Notebook.ACCESS.private,
            editor=Notebook.EDITOR.owner,
        )
        self.notebook.members.add(self.member)

    def test_theme_natural_key(self):
        self.assertEqual(self.theme.natural_key(), ("default",))
        fetched = Theme.objects.get_by_natural_key("default")
        self.assertEqual(fetched, self.theme)
        self.assertEqual(str(self.theme), "default")

    def test_entry_type_natural_key(self):
        self.assertEqual(self.entry_type_text.natural_key(), ("text",))
        fetched = EntryType.objects.get_by_natural_key("text")
        self.assertEqual(fetched, self.entry_type_text)
        self.assertEqual(str(self.entry_type_text), "text")

    def test_notebook_permissions_can_view(self):
        # Private notebook:
        self.assertTrue(self.notebook.can_view(self.owner))
        self.assertTrue(self.notebook.can_view(self.admin))
        self.assertTrue(self.notebook.can_view(self.member))
        self.assertFalse(self.notebook.can_view(self.other))

        # Internal notebook:
        self.notebook.access = Notebook.ACCESS.internal
        self.notebook.save()
        self.assertTrue(self.notebook.can_view(self.other))

        # Public notebook:
        self.notebook.access = Notebook.ACCESS.public
        self.notebook.save()
        self.assertTrue(self.notebook.can_view(None))

    def test_notebook_permissions_can_edit(self):
        # Owner editor:
        self.assertTrue(self.notebook.can_edit(self.owner))
        self.assertTrue(self.notebook.can_edit(self.admin))
        self.assertFalse(self.notebook.can_edit(self.member))
        self.assertFalse(self.notebook.can_edit(self.other))

        # Team editor:
        self.notebook.editor = Notebook.EDITOR.team
        self.notebook.save()
        self.assertTrue(self.notebook.can_edit(self.member))
        self.assertFalse(self.notebook.can_edit(self.other))

        # All users editor:
        self.notebook.editor = Notebook.EDITOR.users
        self.notebook.save()
        self.assertTrue(self.notebook.can_edit(self.other))

    def test_page_uniqueness_and_current(self):
        page1 = Page.objects.create(book=self.notebook)
        self.assertTrue(page1.is_current())
        self.assertIn(self.notebook.name, str(page1))

        # Creating another page on the same book and date must fail UniqueConstraint
        with self.assertRaises(IntegrityError):
            Page.objects.create(book=self.notebook)

    def test_entry_lifecycle_and_tags(self):
        page = Page.objects.create(book=self.notebook)
        entry = Entry.objects.create(
            page=page,
            author=self.owner,
            kind=self.entry_type_text,
            tags=["crystallography", "calibration"],
            text="Initial measurement notes",
        )
        self.assertEqual(entry.tags, ["crystallography", "calibration"])
        self.assertEqual(entry.tag_string(), "crystallography,calibration")
        self.assertTrue(entry.is_editable())
        self.assertTrue(entry.can_edit(self.owner))
        self.assertFalse(entry.can_edit(self.other))
        self.assertTrue(entry.can_view(self.owner))

        # Tag field DB round-trip:
        entry.refresh_from_db()
        self.assertEqual(entry.tags, ["crystallography", "calibration"])

    def test_annotation_functionality(self):
        page = Page.objects.create(book=self.notebook)
        entry = Entry.objects.create(
            page=page,
            author=self.owner,
            kind=self.entry_type_text,
            text="Sample collected with 12 keV",
        )
        highlight = Annotation.objects.create(
            kind=Annotation.ANNOTATION_TYPE.highlight,
            entry=entry,
            node_index=1,
            selections=["12 keV"],
            author=self.member,
        )
        comment = Annotation.objects.create(
            kind=Annotation.ANNOTATION_TYPE.comment,
            entry=entry,
            node_index=1,
            text="Verify beam energy calibration",
            author=self.owner,
        )

        self.assertEqual(entry.annotations.highlights().count(), 1)
        self.assertEqual(entry.annotations.comments().count(), 1)

        payload = highlight.json()
        self.assertEqual(payload["author"], "@member")
        self.assertEqual(payload["type"], "highlight")
        self.assertEqual(payload["selections"], ["12 keV"])

        # Entry with annotations is no longer editable by author
        self.assertFalse(entry.is_editable())
        self.assertFalse(entry.can_edit(self.owner))

    def test_string_list_field_and_form_field(self):
        field = StringListField()
        self.assertEqual(field.to_python(None), [])
        self.assertEqual(field.to_python("<one><two>"), ["one", "two"])
        self.assertEqual(field.get_prep_value(["alpha", "beta"]), "<alpha><beta>")

        form_field = DelimitedTextFormField()
        self.assertEqual(form_field.to_python("a, b; c"), ["a", "b", "c"])
        self.assertEqual(form_field.prepare_value(["x", "y"]), "x; y")

    def test_utils_clean_json(self):
        data = {
            "data": {
                "0": [0.1234567, 0.1234568],
                "1": [1.0, 2.0],
            }
        }
        cleaned = clean_json(json.dumps(data))
        parsed = json.loads(cleaned)
        self.assertIn("data", parsed)
        self.assertEqual(parsed["data"]["1"], [1.0, 2.0])

    def test_utils_time_helpers(self):
        now = timezone.now()
        self.assertEqual(timeish(now), "now")
        self.assertEqual(timeish(now - timedelta(minutes=5)), "5min")
        self.assertEqual(timeish(now - timedelta(hours=3)), "3h")

        simple = simpletime(now)
        self.assertTrue(len(simple) > 0)

        # Fuzzy time queries:
        q_past = fuzzy_time("< 2 days", field="created")
        self.assertTrue(bool(q_past))


if __name__ == "__main__":
    unittest.main()
