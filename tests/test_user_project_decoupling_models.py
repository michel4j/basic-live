import unittest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from tests import setup_django
setup_django()

from basiclive.core.lims.models import (
    User as LimsUser,
    Project,
    ProjectMembership,
    SSHKey,
    ActivityLog,
)
from basiclive.core.acl.models import AccessList, Access
from basiclive.core.crm.models import SupportRecord
from basiclive.core.schedule.models import BeamlineSupport, Beamtime
from basiclive.core.notebooks.models import Notebook
from django.core.management import call_command


class DataModelsDecouplingTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        call_command('migrate', verbosity=0)
        super().setUpClass()
    def test_auth_user_model_is_lims_user(self):
        User = get_user_model()
        self.assertEqual(settings.AUTH_USER_MODEL, "lims.User")
        self.assertEqual(User, LimsUser)

    def test_user_creation_and_fields(self):
        user = LimsUser.objects.create_user(
            username="jdoe",
            email="jdoe@example.org",
            password="securepassword123",
            name="John Doe",
        )
        self.assertEqual(user.username, "jdoe")
        self.assertEqual(user.email, "jdoe@example.org")
        self.assertEqual(user.name, "John Doe")
        self.assertEqual(str(user), "John Doe")
        self.assertTrue(user.check_password("securepassword123"))

    def test_project_model_structure_and_pi_relationship(self):
        pi = LimsUser.objects.create_user(
            username="dr_smith",
            email="smith@example.org",
            password="pass",
            name="Dr. Smith",
        )
        project = Project.objects.create(
            name="biomx-2026",
            pi=pi,
        )
        self.assertEqual(project.name, "biomx-2026")
        self.assertEqual(project.pi, pi)
        self.assertIn(project, pi.led_projects.all())

        # Saving project with PI should ensure membership with role PI
        self.assertTrue(project.memberships.filter(user=pi, role=ProjectMembership.Role.PI).exists())
        self.assertIn(pi, project.members.all())

    def test_project_membership_roles_and_uniqueness(self):
        pi = LimsUser.objects.create_user(username="lead_pi", email="lead@example.org")
        researcher = LimsUser.objects.create_user(username="member_jane", email="jane@example.org")
        project = Project.objects.create(name="proj-alpha", pi=pi)

        membership = ProjectMembership.objects.create(
            user=researcher,
            project=project,
            role=ProjectMembership.Role.CO_INVESTIGATOR,
        )
        self.assertEqual(membership.role, ProjectMembership.Role.CO_INVESTIGATOR)
        self.assertEqual(membership.get_role_display(), "Co-Investigator")
        self.assertIn(researcher, project.members.all())

        # Duplicate membership should raise IntegrityError
        with self.assertRaises(IntegrityError):
            ProjectMembership.objects.create(
                user=researcher,
                project=project,
                role=ProjectMembership.Role.MEMBER,
            )

    def test_sshkey_model_user_foreign_key(self):
        user = LimsUser.objects.create_user(username="keys_user", email="keys@example.org")
        key = SSHKey.objects.create(
            name="laptop-key",
            key="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIG... user@host",
            user=user,
        )
        self.assertEqual(key.user, user)
        self.assertIn(key, user.sshkeys.all())
        self.assertTrue(key.fingerprint())

    def test_acl_models_user_references(self):
        user = LimsUser.objects.create_user(username="acl_user", email="acl@example.org")
        access_list = AccessList.objects.create(
            name="Workstation-1",
            address="10.0.0.1",
            active=True,
        )
        access_list.users.add(user)
        self.assertIn(user, access_list.users.all())

        access = Access.objects.create(
            name="conn-1",
            user=user,
            userlist=access_list,
        )
        self.assertEqual(access.user, user)

    def test_crm_and_schedule_user_and_project_references(self):
        staff_user = LimsUser.objects.create_user(username="beamline_staff", email="staff@example.org")
        pi_user = LimsUser.objects.create_user(username="pi_user", email="pi@example.org")
        project = Project.objects.create(name="exp-42", pi=pi_user)

        # BeamlineSupport staff references User
        support = BeamlineSupport(staff=staff_user, date="2026-10-01")
        self.assertEqual(support.staff, staff_user)

        # Beamtime references Project
        beamtime = Beamtime(project=project)
        self.assertEqual(beamtime.project, project)

        # SupportRecord staff references User, project references Project
        record = SupportRecord(staff=staff_user, project=project)
        self.assertEqual(record.staff, staff_user)
        self.assertEqual(record.project, project)

    def test_activity_log_user_and_project_references(self):
        user = LimsUser.objects.create_user(username="active_user", email="active@example.org")
        project = Project.objects.create(name="active-proj", pi=user)

        log = ActivityLog(user=user, project=project, action_type=ActivityLog.TYPE.LOGIN, ip_number="127.0.0.1")
        self.assertEqual(log.user, user)
        self.assertEqual(log.project, project)

    def test_data_migration_function(self):
        import importlib
        from django.apps import apps
        migration_0104 = importlib.import_module("basiclive.core.lims.migrations.0104_migrate_project_users_data")
        migrate_project_data_to_users = migration_0104.migrate_project_data_to_users

        legacy_proj = Project.objects.create(
            name="legacy-proj",
            username="legacy_lead",
            first_name="Legacy",
            last_name="Leader",
            email="lead@legacy.org",
        )
        legacy_key = SSHKey.objects.create(
            name="legacy-key",
            key="ssh-rsa AAAAB3... lead@host",
            project=legacy_proj,
        )

        migrate_project_data_to_users(apps, None)

        legacy_proj.refresh_from_db()
        legacy_key.refresh_from_db()

        self.assertIsNotNone(legacy_proj.pi)
        self.assertEqual(legacy_proj.pi.username, "legacy_lead")
        self.assertEqual(legacy_proj.pi.email, "lead@legacy.org")
        self.assertEqual(legacy_key.user, legacy_proj.pi)
        self.assertTrue(
            ProjectMembership.objects.filter(
                user=legacy_proj.pi,
                project=legacy_proj,
                role=ProjectMembership.Role.PI
            ).exists()
        )

