import json
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.template import Context, Template, loader
from django.test import RequestFactory, TestCase, override_settings
from django.urls import include, path
from django.utils import timezone

from tests import setup_django

setup_django()

import basiclive.core.notebooks as notebooks_pkg
from basiclive.core.notebooks.models import (
    Entry,
    EntryType,
    Notebook,
)

User = get_user_model()

from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", include("basiclive.core.lims.urls")),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("notebooks/", include("basiclive.core.notebooks.urls")),
]


@override_settings(ROOT_URLCONF="tests.test_notebooks_templates")
class NotebookTemplatesTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        call_command('migrate', verbosity=0)
        super().setUpClass()

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="password123", name="Test User")
        self.text_type, _ = EntryType.objects.get_or_create(name="Text")
        self.data_type, _ = EntryType.objects.get_or_create(name="Data")
        self.file_type, _ = EntryType.objects.get_or_create(name="File")
        self.sketch_type, _ = EntryType.objects.get_or_create(name="Sketch")
        self.image_type, _ = EntryType.objects.get_or_create(name="Image")
        self.video_type, _ = EntryType.objects.get_or_create(name="Video")

        self.notebook = Notebook.objects.create(
            name="test-nb",
            title="Test Notebook",
            description="Test notebook description",
            owner=self.user,
            access=Notebook.ACCESS.public,
            editor=Notebook.EDITOR.owner,
        )

        self.today = timezone.localdate(timezone.now())
        self.entry = Entry.objects.create(
            notebook=self.notebook,
            created=timezone.now(),
            author=self.user,
            text="Hello **Markdown** world!",
            kind=self.text_type,
            tags=["sample", "test"],
        )

    def test_notebooks_templatetags_direct(self):
        """Test notebooks template tags and filters directly."""
        template = Template(
            "{% load bl_notebooks %}"
            "{{ text|clean_json }}"
            "{{ dt|simpletime }}"
            "{{ dt|timeish }}"
            "{{ data|json }}"
        )
        ctx = Context({
            "text": '{"a": 1}',
            "dt": timezone.now(),
            "data": {"key": "value"},
        })
        rendered = template.render(ctx)
        self.assertIn('"a":1', rendered)
        self.assertIn('"key": "value"', rendered)

    def test_load_data_and_plot_axes_tags(self):
        """Test load_data and plot_axes templatetags on tabular data entry."""
        table_json = json.dumps({
            "headers": ["Time", "Intensity", "Label"],
            "data": {
                "0": [0.0, 1.0, 2.0],
                "1": [10.5, 20.3, 30.1],
                "2": ["A", "B", "C"],
            }
        })
        data_entry = Entry.objects.create(
            notebook=self.notebook,
            created=timezone.now(),
            author=self.user,
            text=table_json,
            kind=self.data_type,
        )
        template = Template(
            "{% load bl_notebooks %}"
            "{% load_data entry as d %}"
            "{% plot_axes entry as axes %}"
            "Headers: {{ d.headers|join:',' }}; Axes: {{ axes|join:',' }}"
        )
        rendered = template.render(Context({"entry": data_entry}))
        self.assertIn("Headers: Time,Intensity,Label", rendered)
        self.assertIn("Axes: Time,Intensity", rendered)

    def test_render_entries_templates(self):
        """Verify all entry kind templates render without syntax errors."""
        request = self.factory.get("/")
        request.user = self.user

        for kind in ["Text", "Data", "File", "Sketch", "Image", "Video"]:
            t = loader.get_template(f"notebooks/entries/{kind.lower()}.html")
            data_text = '{"headers": ["X", "Y"], "data": {"0": [1, 2], "1": [3, 4]}}' if kind == "Data" else "Content"
            entry_obj = Entry.objects.create(
                notebook=self.notebook,
                created=timezone.now(),
                author=self.user,
                text=data_text,
                kind=EntryType.objects.get(name=kind),
            )
            rendered = t.render({"entry": entry_obj, "notebook": self.notebook, "user": self.user}, request)
            self.assertIn(f"entry-{kind}", rendered)

    def test_render_notebook_search_template(self):
        """Verify notebook_search.html renders results correctly."""
        request = self.factory.get("/notebooks/search/?q=test")
        request.user = self.user

        t_search = loader.get_template("notebooks/notebook_search.html")
        rendered = t_search.render({"notebooks": [self.notebook], "entries": [self.entry]}, request)
        self.assertIn(self.notebook.title, rendered)
        self.assertIn("NOTEBOOKS", rendered)

    def test_render_notebook_list_template(self):
        """Verify notebook_list.html renders cleanly."""
        request = self.factory.get("/notebooks/")
        request.user = self.user

        t_list = loader.get_template("notebooks/notebook_list.html")
        rendered = t_list.render({
            "notebooks": Notebook.objects.all(),
        }, request)
        self.assertIn("Notebooks", rendered)
        self.assertIn(self.notebook.title, rendered)

    def test_render_notebook_detail_template(self):
        """Verify notebook.html renders cleanly extending lims/base.html."""
        request = self.factory.get(f"/notebooks/{self.notebook.pk}/")
        request.user = self.user

        t_detail = loader.get_template("notebooks/notebook.html")
        rendered = t_detail.render({
            "notebook": self.notebook,
            "object": self.notebook,
            "entries": [self.entry],
            "user": self.user,
        }, request)
        self.assertIn(self.notebook.title, rendered)
        self.assertIn("notebook-content", rendered)
        self.assertIn("entry-selector", rendered)

    def test_bootstrap_5_compliance_in_templates(self):
        """Ensure no legacy Bootstrap 4 classes or obsolete tags exist in templates."""
        templates_dir = Path(notebooks_pkg.__file__).parent / "templates" / "notebooks"
        html_files = list(templates_dir.rglob("*.html"))
        self.assertTrue(len(html_files) > 0, "Template files must exist")

        legacy_patterns = [
            'data-toggle="',
            'text-right',
            'float-right',
            'custom-select',
            '{% load md2 %}',
        ]

        for path in html_files:
            content = path.read_text(encoding="utf-8")
            for pattern in legacy_patterns:
                self.assertNotIn(
                    pattern,
                    content,
                    f"Found legacy pattern '{pattern}' in {path.relative_to(templates_dir)}"
                )
