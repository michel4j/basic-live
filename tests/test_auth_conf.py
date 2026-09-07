import unittest
from unittest.mock import MagicMock, patch

from tests import setup_django

setup_django()

from django.test import SimpleTestCase, override_settings

from basiclive.auth.cas.conf import settings as cas_settings
from basiclive.auth.ldap.conf import settings as ldap_settings
from basiclive.auth.ldap.models import is_directory_management_enabled
from basiclive.auth.ldap import slap


class LdapConfTests(SimpleTestCase):
    def test_default_settings(self):
        self.assertEqual(ldap_settings.BASE_DN, "dc=demo1,dc=freeipa,dc=org")
        self.assertEqual(ldap_settings.SERVER_URI, "ipa.demo1.freeipa.org")
        self.assertIsNone(ldap_settings.MANAGER_DN)
        self.assertIsNone(ldap_settings.MANAGER_SECRET)
        self.assertEqual(ldap_settings.USER_TABLE, "ou=People")
        self.assertEqual(ldap_settings.USER_ROOT, "/home")
        self.assertEqual(ldap_settings.GROUP_TABLE, "ou=Groups")
        self.assertEqual(ldap_settings.USER_SHELL, "/bin/bash")
        self.assertEqual(ldap_settings.WORDS_DICTIONARY, "/usr/share/dict/words")
        self.assertEqual(ldap_settings.PASSPHRASE_SEPARATORS, " -/")
        self.assertIs(ldap_settings.MANAGE_DIRECTORY, False)
        self.assertIs(ldap_settings.SEND_EMAILS, False)
        self.assertEqual(ldap_settings.ADMIN_UIDS, [2000])
        self.assertEqual(ldap_settings.AUTH_OBJECT_CLASS, "posixAccount")
        self.assertEqual(ldap_settings.AUTH_USER_LOOKUP_FIELDS, ("username",))
        self.assertIs(ldap_settings.AUTH_USE_TLS, True)
        self.assertIn("username", ldap_settings.AUTH_USER_FIELDS)

    def test_prefixed_and_unprefixed_attribute_access(self):
        # Accessing with and without LDAP_ prefix should resolve identically
        self.assertEqual(ldap_settings.MANAGE_DIRECTORY, False)
        self.assertEqual(ldap_settings.LDAP_MANAGE_DIRECTORY, False)

        self.assertEqual(ldap_settings.SERVER_URI, "ipa.demo1.freeipa.org")
        self.assertEqual(ldap_settings.LDAP_SERVER_URI, "ipa.demo1.freeipa.org")

        self.assertEqual(ldap_settings.BASE_DN, "dc=demo1,dc=freeipa,dc=org")
        self.assertEqual(ldap_settings.LDAP_BASE_DN, "dc=demo1,dc=freeipa,dc=org")

    def test_override_via_basiclive_ldap_unprefixed_keys(self):
        with override_settings(
            BASICLIVE_LDAP={
                "MANAGE_DIRECTORY": True,
                "SERVER_URI": "custom-ldap.facility.ca",
                "BASE_DN": "dc=facility,dc=ca",
            }
        ):
            self.assertIs(ldap_settings.MANAGE_DIRECTORY, True)
            self.assertIs(ldap_settings.LDAP_MANAGE_DIRECTORY, True)
            self.assertEqual(ldap_settings.SERVER_URI, "custom-ldap.facility.ca")
            self.assertEqual(ldap_settings.LDAP_SERVER_URI, "custom-ldap.facility.ca")
            self.assertEqual(ldap_settings.BASE_DN, "dc=facility,dc=ca")

        # Restored
        self.assertIs(ldap_settings.MANAGE_DIRECTORY, False)
        self.assertEqual(ldap_settings.SERVER_URI, "ipa.demo1.freeipa.org")

    def test_override_via_basiclive_ldap_prefixed_keys(self):
        with override_settings(
            BASICLIVE_LDAP={
                "LDAP_MANAGE_DIRECTORY": True,
                "LDAP_SERVER_URI": "prefixed-ldap.facility.ca",
            }
        ):
            self.assertIs(ldap_settings.MANAGE_DIRECTORY, True)
            self.assertIs(ldap_settings.LDAP_MANAGE_DIRECTORY, True)
            self.assertEqual(ldap_settings.SERVER_URI, "prefixed-ldap.facility.ca")
            self.assertEqual(ldap_settings.LDAP_SERVER_URI, "prefixed-ldap.facility.ca")

        # Restored
        self.assertIs(ldap_settings.MANAGE_DIRECTORY, False)
        self.assertEqual(ldap_settings.SERVER_URI, "ipa.demo1.freeipa.org")

    def test_override_via_fallback_namespace(self):
        with override_settings(BASICLIVE_AUTH_LDAP={"MANAGE_DIRECTORY": True}):
            self.assertIs(ldap_settings.MANAGE_DIRECTORY, True)

        self.assertIs(ldap_settings.MANAGE_DIRECTORY, False)

    def test_is_directory_management_enabled(self):
        # Default is False
        self.assertFalse(is_directory_management_enabled())

        # Enabled via MANAGE_DIRECTORY
        with override_settings(BASICLIVE_LDAP={"MANAGE_DIRECTORY": True}):
            self.assertTrue(is_directory_management_enabled())

        # Enabled via LDAP_MANAGE_DIRECTORY
        with override_settings(BASICLIVE_LDAP={"LDAP_MANAGE_DIRECTORY": True}):
            self.assertTrue(is_directory_management_enabled())

        # Enabled via MANAGER_DN
        with override_settings(BASICLIVE_LDAP={"MANAGER_DN": "cn=admin,dc=example,dc=org"}):
            self.assertTrue(is_directory_management_enabled())

        # Enabled via LDAP_MANAGER_DN
        with override_settings(BASICLIVE_LDAP={"LDAP_MANAGER_DN": "cn=admin,dc=example,dc=org"}):
            self.assertTrue(is_directory_management_enabled())

        # Reverts to False
        self.assertFalse(is_directory_management_enabled())

    def test_slap_directory_helpers(self):
        mock_server = MagicMock()
        with patch.object(slap, "Server", return_value=mock_server), \
             patch.object(slap, "ldap3", MagicMock()):
            d = slap.Directory()
            self.assertEqual(d._base_dn(), "dc=demo1,dc=freeipa,dc=org")
            self.assertEqual(d._user_table(), "ou=People")
            self.assertEqual(d._group_table(), "ou=Groups")
            self.assertEqual(d._user_root(), "/home")
            self.assertEqual(d._user_shell(), "/bin/bash")

            with override_settings(BASICLIVE_LDAP={"BASE_DN": "dc=overridden,dc=org"}):
                self.assertEqual(d._base_dn(), "dc=overridden,dc=org")


class CasConfTests(SimpleTestCase):
    def test_default_settings(self):
        self.assertEqual(cas_settings.SERVER_URL, "https://cas-test.clsi.ca/")
        self.assertEqual(cas_settings.SERVICE_DESCRIPTION, "LIVE")
        self.assertIs(cas_settings.LOGOUT_COMPLETELY, True)
        self.assertIs(cas_settings.CREATE_USER, True)
        self.assertEqual(cas_settings.REDIRECT_URL, "login")
        self.assertEqual(cas_settings.LOGIN_URL_NAME, "login")
        self.assertEqual(cas_settings.LOGOUT_URL_NAME, "logout")

    def test_prefixed_and_unprefixed_attribute_access(self):
        self.assertEqual(cas_settings.SERVER_URL, "https://cas-test.clsi.ca/")
        self.assertEqual(cas_settings.CAS_SERVER_URL, "https://cas-test.clsi.ca/")
        self.assertIs(cas_settings.CREATE_USER, True)
        self.assertIs(cas_settings.CAS_CREATE_USER, True)

    def test_override_via_basiclive_cas(self):
        with override_settings(
            BASICLIVE_CAS={
                "SERVER_URL": "https://cas.facility.ca/",
                "CREATE_USER": False,
                "SERVICE_DESCRIPTION": "MySynchrotron",
            }
        ):
            self.assertEqual(cas_settings.SERVER_URL, "https://cas.facility.ca/")
            self.assertEqual(cas_settings.CAS_SERVER_URL, "https://cas.facility.ca/")
            self.assertIs(cas_settings.CREATE_USER, False)
            self.assertIs(cas_settings.CAS_CREATE_USER, False)
            self.assertEqual(cas_settings.SERVICE_DESCRIPTION, "MySynchrotron")

        # Restored
        self.assertEqual(cas_settings.SERVER_URL, "https://cas-test.clsi.ca/")
        self.assertIs(cas_settings.CREATE_USER, True)

    def test_override_via_fallback_namespace(self):
        with override_settings(BASICLIVE_AUTH_CAS={"SERVER_URL": "https://auth-cas.org/"}):
            self.assertEqual(cas_settings.SERVER_URL, "https://auth-cas.org/")

        self.assertEqual(cas_settings.SERVER_URL, "https://cas-test.clsi.ca/")


if __name__ == "__main__":
    unittest.main()
