from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from basiclive.core.crm.forms import SupportEntryForm
from basiclive.core.crm.models import SupportArea, SupportRecord
from basiclive.core.lims.models import Beamline, Project, ProjectType

User = get_user_model()


class SupportModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="user@example.org", is_staff=True)
        self.project = Project.objects.create(name="Research Project", pi=self.user)
        self.beamline = Beamline.objects.create(name="Beamline 1", acronym="BL1")
        self.area = SupportArea.objects.create(name="Optics & Mirrors", external=False)

    def test_support_area_creation_and_str(self):
        self.assertEqual(str(self.area), "Optics & Mirrors")
        self.assertFalse(self.area.external)
        self.assertFalse(self.area.user_feedback)

    def test_support_record_creation_with_area(self):
        record = SupportRecord.objects.create(
            kind=SupportRecord.TYPE.problem,
            area=self.area,
            staff=self.user,
            project=self.project,
            beamline=self.beamline,
            lost_time=1.5,
            comments="Mirror alignment lost",
            staff_comments="Realigned mirror motors",
        )
        self.assertEqual(record.area, self.area)
        self.assertEqual(record.staff, self.user)
        self.assertEqual(str(record), f"{self.user} | {self.beamline} | {self.project}")
        self.assertEqual(record.area_names, "Optics & Mirrors")

    def test_support_record_without_area(self):
        record = SupportRecord.objects.create(
            kind=SupportRecord.TYPE.info,
            staff=self.user,
            project=self.project,
            beamline=self.beamline,
        )
        self.assertIsNone(record.area)
        self.assertEqual(record.area_names, "")

    def test_support_area_reverse_records_accessor(self):
        record1 = SupportRecord.objects.create(
            kind=SupportRecord.TYPE.problem,
            area=self.area,
            staff=self.user,
            project=self.project,
            beamline=self.beamline,
            lost_time=1.0,
        )
        record2 = SupportRecord.objects.create(
            kind=SupportRecord.TYPE.info,
            area=self.area,
            staff=self.user,
            project=self.project,
            beamline=self.beamline,
            lost_time=0.0,
        )
        self.assertEqual(list(self.area.records.order_by("pk")), [record1, record2])


class SupportFormTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="staffuser", email="staff@example.org", is_staff=True
        )
        self.user = User.objects.create_user(username="scienceuser", email="user@example.org")
        self.user_project = Project.objects.create(name="User Group", pi=self.user)
        self.beamline = Beamline.objects.create(name="Beamline 1", acronym="BL1")
        self.area = SupportArea.objects.create(name="Detectors")

    def test_support_entry_form_valid(self):
        form_data = {
            "kind": "problem",
            "area": self.area.pk,
            "staff": self.staff_user.pk,
            "project": self.user_project.pk,
            "beamline": self.beamline.pk,
            "lost_time": 2.5,
            "comments": "Detector readout error",
            "staff_comments": "Power cycled controller",
        }
        form = SupportEntryForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        record = form.save()
        self.assertEqual(record.area, self.area)
        self.assertEqual(record.staff, self.staff_user)
        self.assertEqual(record.lost_time, 2.5)

    def test_support_entry_form_layout_contains_area(self):
        form = SupportEntryForm()
        self.assertIn("area", form.fields)
        layout_fields = [
            field_name
            for row in form.body.layout.fields if hasattr(row, 'fields')
            for f in row.fields
            for field_name in (f.fields if hasattr(f, 'fields') else [f])
        ]
        self.assertIn("area", layout_fields)


class SupportViewTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="adminuser", email="admin@example.org", password="adminpassword"
        )
        self.client.force_login(self.admin_user)

        self.staff_user = User.objects.create_user(
            username="staffmember", email="staffmember@example.org", is_staff=True
        )
        self.user_project = Project.objects.create(name="Science Group", pi=self.admin_user)
        self.beamline = Beamline.objects.create(name="Beamline 1", acronym="BL1")
        self.area1 = SupportArea.objects.create(name="Optics")
        self.area2 = SupportArea.objects.create(name="Cryo")

        self.record1 = SupportRecord.objects.create(
            kind=SupportRecord.TYPE.problem,
            area=self.area1,
            staff=self.staff_user,
            project=self.user_project,
            beamline=self.beamline,
            lost_time=1.0,
            comments="Optics glitch",
        )
        self.record2 = SupportRecord.objects.create(
            kind=SupportRecord.TYPE.info,
            area=self.area2,
            staff=self.staff_user,
            project=self.user_project,
            beamline=self.beamline,
            lost_time=0.0,
            comments="Cryo refill",
        )

    def test_support_record_list_view(self):
        response = self.client.get(reverse("supportrecord-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Optics")
        self.assertContains(response, "Cryo")

    def test_support_record_list_filter_by_area(self):
        response = self.client.get(reverse("supportrecord-list"), {"area__id__exact": self.area1.pk})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.record1, response.context["object_list"])
        self.assertNotIn(self.record2, response.context["object_list"])

    def test_support_record_create_view(self):
        post_data = {
            "kind": "problem",
            "area": self.area1.pk,
            "staff": self.staff_user.pk,
            "project": self.user_project.pk,
            "beamline": self.beamline.pk,
            "lost_time": 0.75,
            "comments": "Motor stalled",
            "staff_comments": "Reset stage",
        }
        response = self.client.post(reverse("new-supportrecord"), post_data)
        self.assertEqual(response.status_code, 200)  # ModalForm returns 200 with JSON or redirect
        self.assertTrue(SupportRecord.objects.filter(comments="Motor stalled", area=self.area1, staff=self.staff_user).exists())

    def test_support_record_create_view_initial_staff(self):
        response = self.client.get(reverse("new-supportrecord"))
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.initial.get("staff"), self.admin_user)

    def test_support_record_edit_view(self):
        post_data = {
            "kind": "problem",
            "area": self.area2.pk,
            "staff": self.staff_user.pk,
            "project": self.user_project.pk,
            "beamline": self.beamline.pk,
            "lost_time": 2.0,
            "comments": "Optics glitch updated to cryo",
            "staff_comments": "Switched area",
        }
        response = self.client.post(reverse("supportrecord-edit", kwargs={"pk": self.record1.pk}), post_data)
        self.assertEqual(response.status_code, 200)
        self.record1.refresh_from_db()
        self.assertEqual(self.record1.area, self.area2)
        self.assertEqual(self.record1.lost_time, 2.0)
        self.assertEqual(self.record1.staff, self.staff_user)

    def test_support_record_stats_view(self):
        response = self.client.get(reverse("supportrecord-stats"))
        self.assertEqual(response.status_code, 200)


class SupportMigrationLogicTests(TestCase):
    def test_populate_area_duplicates_multiarea_records(self):
        import importlib
        migration_module = importlib.import_module("basiclive.core.crm.migrations.0085_populate_supportrecord_area")
        populate_area_from_areas = migration_module.populate_area_from_areas

        area_a = SupportArea.objects.create(name="Area Alpha")
        area_b = SupportArea.objects.create(name="Area Beta")
        user = User.objects.create_user(username="miguser", email="mig@example.org")
        project = Project.objects.create(name="Mig Project", pi=user)
        beamline = Beamline.objects.create(name="Mig BL", acronym="MBL")

        # Create record with area_a
        rec = SupportRecord.objects.create(
            kind="problem",
            area=None,
            project=project,
            beamline=beamline,
            lost_time=1.0,
            comments="Original record",
        )

        class MockRecord:
            def __init__(self, record, areas_list):
                self.record = record
                self.pk = record.pk
                self.areas_list = areas_list
                self.kind = record.kind
                self.staff_id = record.staff_id
                self.user_id = None
                self.project_id = record.project_id
                self.beamline_id = record.beamline_id
                self.comments = record.comments
                self.lost_time = record.lost_time
                self.staff_comments = record.staff_comments
                self.created = record.created
                self.modified = record.modified

            @property
            def areas(self):
                class MockAreas:
                    def __init__(self, items):
                        self.items = items

                    def all(self):
                        return self.items
                return MockAreas(self.areas_list)

            def save(self, update_fields=None):
                self.record.area = self.area
                self.record.save(update_fields=update_fields)

        class MockSupportRecordManager:
            def __init__(self, mock_records):
                self.mock_records = mock_records

            def using(self, alias):
                return self

            def all(self):
                return self.mock_records

            def create(self, **kwargs):
                kwargs.pop('user_id', None)
                return SupportRecord.objects.create(**kwargs)

        class MockSupportRecordModel:
            def __init__(self, mock_records):
                self.objects = MockSupportRecordManager(mock_records)

        class MockApps:
            def get_model(self, app_label, model_name):
                return MockSupportRecordModel([MockRecord(rec, [area_a, area_b])])

        class MockSchemaEditor:
            class MockConnection:
                alias = "default"
            connection = MockConnection()

        populate_area_from_areas(MockApps(), MockSchemaEditor())

        records = SupportRecord.objects.filter(project=project).order_by("pk")
        self.assertEqual(records.count(), 2)
        self.assertEqual(records[0].area, area_a)
        self.assertEqual(records[1].area, area_b)
        self.assertEqual(records[1].comments, "Original record")
