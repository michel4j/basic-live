import unittest
from django.core.management import call_command
from django.test import TestCase

from basiclive.core.lims.forms import NewProjectForm, ProjectForm
from basiclive.core.lims.models import (
    User,
    Project,
    ProjectMembership,
    ProjectType,
    Carrier,
)


class ProjectFormsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        call_command('migrate', verbosity=0)
        super().setUpClass()

    def setUp(self):
        self.project_type = ProjectType.objects.create(name="Standard MX")
        self.carrier = Carrier.objects.create(name="FedEx")

        self.pi = User.objects.create_user(
            username="prof_jones",
            email="jones@university.edu",
            name="Prof. Indiana Jones"
        )
        self.co_inv = User.objects.create_user(
            username="dr_marion",
            email="marion@university.edu",
            name="Dr. Marion Ravenwood"
        )
        self.member1 = User.objects.create_user(
            username="sallah",
            email="sallah@cairo.org",
            name="Sallah"
        )
        self.member2 = User.objects.create_user(
            username="shorty",
            email="shorty@club.org",
            name="Short Round"
        )
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.org",
            password="adminpassword"
        )

    def test_new_project_form_successful_creation(self):
        form_data = {
            'name': 'ark-discovery',
            'kind': self.project_type.pk,
            'pi': self.pi.pk,
            'co_investigator': self.co_inv.pk,
            'members': [self.member1.pk, self.member2.pk],
            'alias': 'ARK-PROJECT',
            'contact_person': 'Marion Ravenwood',
            'contact_email': 'logistics@university.edu',
            'contact_phone': '555-019-2834',
            'carrier': self.carrier.pk,
            'account_number': '12345678',
            'shipping_notes': 'Handle with care',
            'organisation': 'Marshall College',
            'department': 'Archaeology',
            'address': '123 University Ave',
            'city': 'Bedford',
            'province': 'CT',
            'country': 'US',
            'postal_code': '06807',
        }
        form = NewProjectForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        project = form.save()

        self.assertEqual(project.name, 'ark-discovery')
        self.assertEqual(project.pi, self.pi)
        self.assertEqual(project.kind, self.project_type)
        self.assertEqual(project.contact_person, 'Marion Ravenwood')
        self.assertEqual(project.contact_email, 'logistics@university.edu')
        self.assertEqual(project.carrier, self.carrier)

        # Check memberships
        pi_membership = ProjectMembership.objects.get(project=project, user=self.pi)
        self.assertEqual(pi_membership.role, ProjectMembership.Role.PI)

        co_membership = ProjectMembership.objects.get(project=project, user=self.co_inv)
        self.assertEqual(co_membership.role, ProjectMembership.Role.CO_INVESTIGATOR)

        m1_membership = ProjectMembership.objects.get(project=project, user=self.member1)
        self.assertEqual(m1_membership.role, ProjectMembership.Role.MEMBER)

        m2_membership = ProjectMembership.objects.get(project=project, user=self.member2)
        self.assertEqual(m2_membership.role, ProjectMembership.Role.MEMBER)

        self.assertEqual(project.memberships.count(), 4)

    def test_new_project_form_requires_pi(self):
        form_data = {
            'name': 'no-pi-project',
            'kind': self.project_type.pk,
        }
        form = NewProjectForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('pi', form.errors)

    def test_new_project_form_deduplicates_pi_and_co_inv_in_members(self):
        # If PI or Co-Investigator is accidentally included in 'members',
        # their higher role should not be overridden to MEMBER.
        form_data = {
            'name': 'overlap-project',
            'kind': self.project_type.pk,
            'pi': self.pi.pk,
            'co_investigator': self.co_inv.pk,
            'members': [self.pi.pk, self.co_inv.pk, self.member1.pk],
        }
        form = NewProjectForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        project = form.save()

        self.assertEqual(project.memberships.count(), 3)
        self.assertEqual(
            ProjectMembership.objects.get(project=project, user=self.pi).role,
            ProjectMembership.Role.PI
        )
        self.assertEqual(
            ProjectMembership.objects.get(project=project, user=self.co_inv).role,
            ProjectMembership.Role.CO_INVESTIGATOR
        )
        self.assertEqual(
            ProjectMembership.objects.get(project=project, user=self.member1).role,
            ProjectMembership.Role.MEMBER
        )

    def test_project_form_edit_existing_project(self):
        project = Project.objects.create(
            name="existing-project",
            pi=self.pi,
            contact_person="Old Contact",
            city="Old Town"
        )
        edit_data = {
            'contact_person': 'New Contact',
            'contact_email': 'new@contact.org',
            'city': 'New Metropolis',
            'country': 'CA',
            'kind': self.project_type.pk,
        }
        form = ProjectForm(instance=project, data=edit_data, user=self.admin)
        self.assertTrue(form.is_valid(), form.errors)
        saved = form.save()

        self.assertEqual(saved.contact_person, 'New Contact')
        self.assertEqual(saved.city, 'New Metropolis')
        self.assertEqual(saved.name, 'existing-project')
        self.assertEqual(saved.pi, self.pi)
