import unittest
from django.conf import settings as django_settings
from django.template import Context, Template
from django.test import SimpleTestCase, override_settings

from basiclive.core.lims.conf import settings as lims_settings


from tests import setup_django
setup_django()


class LimsConfTests(SimpleTestCase):
    def test_default_settings(self):
        self.assertIs(lims_settings.USE_SCHEDULE, True)
        self.assertIs(lims_settings.USE_ACL, True)
        self.assertIs(lims_settings.USE_CRM, True)
        self.assertIs(lims_settings.USE_PUBLICATIONS, True)
        self.assertEqual(lims_settings.MAX_CONTAINER_DEPTH, 2)
        self.assertIs(lims_settings.RESTRICT_DOWNLOADS, False)
        self.assertEqual(lims_settings.LOADER_SELECT_DURATION, 300)
        self.assertEqual(lims_settings.APP_NAME, "BasicLIVE")
        self.assertEqual(lims_settings.BASE_DIR, "/tmp")

    def test_override_via_basiclive_lims(self):
        with override_settings(
            BASICLIVE_LIMS={
                "MAX_CONTAINER_DEPTH": 4,
                "DOWNLOAD_PROXY_URL": "https://custom-proxy.example.com",
                "USE_SCHEDULE": False,
            }
        ):
            self.assertEqual(lims_settings.MAX_CONTAINER_DEPTH, 4)
            self.assertEqual(lims_settings.DOWNLOAD_PROXY_URL, "https://custom-proxy.example.com")
            self.assertIs(lims_settings.USE_SCHEDULE, False)
            # Non-overridden setting keeps default
            self.assertIs(lims_settings.USE_ACL, True)

        # Restores after context exit
        self.assertEqual(lims_settings.MAX_CONTAINER_DEPTH, 2)
        self.assertIs(lims_settings.USE_SCHEDULE, True)

    def test_get_setting_templatetag(self):
        # Test get_setting with exact setting name
        t1 = Template("{% load settings %}{% get_setting 'APP_NAME' %}")
        rendered1 = t1.render(Context({}))
        self.assertEqual(rendered1.strip(), "BasicLIVE")

        # Test get_setting with legacy LIMS_ prefix normalization
        t2 = Template("{% load settings %}{% get_setting 'LIMS_USE_SCHEDULE' %}")
        rendered2 = t2.render(Context({}))
        self.assertEqual(rendered2.strip(), "True")

        # Test get_setting with override
        with override_settings(BASICLIVE_LIMS={"APP_NAME": "FacilityLIVE"}):
            t3 = Template("{% load settings %}{% get_setting 'APP_NAME' %}")
            rendered3 = t3.render(Context({}))
            self.assertEqual(rendered3.strip(), "FacilityLIVE")


if __name__ == "__main__":
    unittest.main()
