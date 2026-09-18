import json
from pathlib import Path
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import include, path, reverse

from tests import setup_django

setup_django()

from basiclive.core.notebooks.forms import NotebookForm
from basiclive.core.notebooks.models import Notebook
import basiclive.core.notebooks as notebooks_pkg

User = get_user_model()

urlpatterns = [
    path("notebooks/", include("basiclive.core.notebooks.urls")),
]


@override_settings(ROOT_URLCONF="tests.test_notebooks_forms")
class NotebookFormsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        call_command('migrate', verbosity=0)
        super().setUpClass()

    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="password123", name="Owner")
        self.member = User.objects.create_user(username="member", password="password123", name="Member")
        self.other = User.objects.create_user(username="other", password="password123", name="Other")
        self.admin = User.objects.create_superuser(username="admin", password="password123", name="Admin")

        self.notebook = Notebook.objects.create(
            name="existing-notebook",
            title="Existing Notebook",
            description="Existing description",
            owner=self.owner,
            access=Notebook.ACCESS.private,
            editor=Notebook.EDITOR.owner,
        )

    def test_notebook_form_create_init(self):
        """Test NotebookForm initialization for a new notebook."""
        form = NotebookForm(user=self.owner)
        self.assertEqual(form.body.title, "Create Notebook")
        self.assertEqual(form.fields['owner'].initial, self.owner)
        self.assertIn("title", form.fields)
        self.assertIn("description", form.fields)

        # Check footer buttons
        buttons = form.footer.layout.fields
        button_labels = [b.content for b in buttons]
        self.assertIn("Save", button_labels)

    def test_notebook_form_edit_init(self):
        """Test NotebookForm initialization for an existing notebook."""
        form = NotebookForm(instance=self.notebook, user=self.owner)
        self.assertEqual(form.body.title, "Edit Notebook")
        self.assertEqual(form.initial['title'], "Existing Notebook")

    def test_notebook_form_owner_restriction_non_superuser(self):
        """Non-superusers should have owner queryset restricted to themselves."""
        form = NotebookForm(user=self.owner)
        owner_pks = list(form.fields['owner'].queryset.values_list('pk', flat=True))
        self.assertEqual(owner_pks, [self.owner.pk])

    def test_notebook_form_superuser_can_assign_any_owner(self):
        """Superusers can assign any user as notebook owner."""
        form = NotebookForm(user=self.admin)
        owner_pks = set(form.fields['owner'].queryset.values_list('pk', flat=True))
        self.assertIn(self.owner.pk, owner_pks)
        self.assertIn(self.member.pk, owner_pks)
        self.assertIn(self.other.pk, owner_pks)

    def test_notebook_form_valid_save(self):
        """Test submitting valid data to NotebookForm saves a new notebook."""
        data = {
            'title': "Brand New Notebook",
            'description': "Details about experiment",
            'owner': self.owner.pk,
            'access': Notebook.ACCESS.internal,
            'editor': Notebook.EDITOR.team,
            'members': [self.member.pk],
        }
        form = NotebookForm(data=data, user=self.owner)
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.title, "Brand New Notebook")
        self.assertEqual(instance.owner, self.owner)
        self.assertIn(self.member, instance.members.all())

    def test_create_notebook_view_get(self):
        """Test GET request to CreateNotebook renders modal form."""
        self.client.force_login(self.owner)
        response = self.client.get(reverse('notebooks:create-notebook'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Notebook")

    def test_create_notebook_view_post(self):
        """Test POST request to CreateNotebook creates a notebook and returns json response."""
        self.client.force_login(self.owner)
        data = {
            'title': "Modal Created Notebook",
            'description': "Created via crisp-modals view",
            'owner': self.owner.pk,
            'access': Notebook.ACCESS.public,
            'editor': Notebook.EDITOR.owner,
        }
        response = self.client.post(reverse('notebooks:create-notebook'), data=data)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn('url', json_data)
        self.assertTrue(Notebook.objects.filter(title="Modal Created Notebook").exists())

    def test_update_notebook_view_get_by_owner(self):
        """Test GET request to UpdateNotebook by owner succeeds."""
        self.client.force_login(self.owner)
        response = self.client.get(
            reverse('notebooks:notebook-edit', kwargs={'pk': self.notebook.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Notebook")

    def test_update_notebook_view_by_owner(self):
        """Test POST request to UpdateNotebook by owner succeeds."""
        self.client.force_login(self.owner)
        data = {
            'title': "Updated Title by Owner",
            'description': "Updated description",
            'owner': self.owner.pk,
            'access': Notebook.ACCESS.private,
            'editor': Notebook.EDITOR.owner,
        }
        response = self.client.post(
            reverse('notebooks:notebook-edit', kwargs={'pk': self.notebook.pk}),
            data=data
        )
        self.assertEqual(response.status_code, 200)
        self.notebook.refresh_from_db()
        self.assertEqual(self.notebook.title, "Updated Title by Owner")

    def test_update_notebook_view_permission_denied_for_non_owner(self):
        """Non-owners (who are not superusers) should be denied editing access."""
        self.client.force_login(self.other)
        response = self.client.get(
            reverse('notebooks:notebook-edit', kwargs={'pk': self.notebook.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_no_is_ajax_references(self):
        """Verify that deprecated request.is_ajax() is completely purged."""
        pkg_dir = Path(notebooks_pkg.__file__).parent
        for py_file in pkg_dir.glob("*.py"):
            with open(py_file, "r") as f:
                content = f.read()
            self.assertNotIn("is_ajax", content, f"Found deprecated is_ajax in {py_file.name}")
