import unittest
from unittest.mock import MagicMock

from tests import setup_django

setup_django()

from django.test import SimpleTestCase, override_settings

from basiclive.core.crm.conf import settings as crm_settings
from basiclive.core.lims.conf import settings as lims_settings
from basiclive.core.publications.conf import settings as pub_settings
from basiclive.core.publications.utils import get_search_json, tag_function
from basiclive.core.publications.views import PDBEntryList


class PublicationsConfTests(SimpleTestCase):
    def test_default_settings(self):
        self.assertEqual(pub_settings.PDB_FACILITY_ACRONYM, "CLSI")
        self.assertEqual(pub_settings.CONTACT_EMAIL, "admin@example.com")
        self.assertIsNone(pub_settings.CROSSREF_API_KEY)
        self.assertEqual(pub_settings.CROSSREF_THROTTLE, 1)
        self.assertEqual(pub_settings.CROSSREF_BATCH_SIZE, 10)
        self.assertIsNone(pub_settings.GOOGLE_API_KEY)
        self.assertEqual(pub_settings.PDB_SEARCH_URL, "https://search.rcsb.org/rcsbsearch/v2/query")
        self.assertEqual(pub_settings.PDB_REPORT_URL, "https://data.rcsb.org/graphql")
        self.assertEqual(pub_settings.GOOGLE_BOOKS_API, "https://www.googleapis.com/books/v1/volumes")
        self.assertEqual(pub_settings.SCIMAGO_URL, "https://www.scimagojr.com/journalrank.php")
        self.assertEqual(pub_settings.PDB_URL_TEMPLATE, "https://www.rcsb.org/structure/{}")
        self.assertEqual(pub_settings.YEAR_FILTER_START, 2005)
        self.assertTrue(pub_settings.LOCAL_DIR)

        # Default tag function behavior
        entry = {"diffrn_source.pdbx_synchrotron_beamline": "Synchrotron 08B1-1"}
        self.assertEqual(tag_function(entry), ["08B1-1"])

        # Default search JSON uses PDB_FACILITY_ACRONYM
        search_json = get_search_json()
        self.assertEqual(search_json["query"]["parameters"]["value"], "CLSI")

    def test_override_via_basiclive_publications(self):
        with override_settings(
            BASICLIVE_PUBLICATIONS={
                "PDB_FACILITY_ACRONYM": "ALS",
                "CONTACT_EMAIL": "beamline@lbl.gov",
                "CROSSREF_THROTTLE": 3,
                "CROSSREF_BATCH_SIZE": 50,
                "GOOGLE_API_KEY": "secret-key",
                "PDB_URL_TEMPLATE": "https://custom.rcsb.org/entry/{}",
                "YEAR_FILTER_START": 2012,
                "PDB_TAG_FUNCTION": lambda e: ["CUSTOM_TAG"],
            }
        ):
            self.assertEqual(pub_settings.PDB_FACILITY_ACRONYM, "ALS")
            self.assertEqual(pub_settings.CONTACT_EMAIL, "beamline@lbl.gov")
            self.assertEqual(pub_settings.CROSSREF_THROTTLE, 3)
            self.assertEqual(pub_settings.CROSSREF_BATCH_SIZE, 50)
            self.assertEqual(pub_settings.GOOGLE_API_KEY, "secret-key")
            self.assertEqual(pub_settings.PDB_URL_TEMPLATE, "https://custom.rcsb.org/entry/{}")
            self.assertEqual(pub_settings.YEAR_FILTER_START, 2012)

            # Custom tag function
            self.assertEqual(tag_function({}), ["CUSTOM_TAG"])

            # Search json dynamically reflects acronym
            search_json = get_search_json()
            self.assertEqual(search_json["query"]["parameters"]["value"], "ALS")

        # Restores defaults after context exit
        self.assertEqual(pub_settings.PDB_FACILITY_ACRONYM, "CLSI")
        self.assertEqual(pub_settings.CONTACT_EMAIL, "admin@example.com")
        self.assertEqual(pub_settings.CROSSREF_THROTTLE, 1)
        self.assertEqual(pub_settings.CROSSREF_BATCH_SIZE, 10)
        self.assertIsNone(pub_settings.GOOGLE_API_KEY)
        self.assertEqual(pub_settings.PDB_URL_TEMPLATE, "https://www.rcsb.org/structure/{}")
        self.assertEqual(pub_settings.YEAR_FILTER_START, 2005)

    def test_views_pdb_url_template_dynamic_resolution(self):
        mock_obj = MagicMock()
        mock_obj.code = "1ABC"
        view = PDBEntryList()

        self.assertEqual(view.get_link_url(mock_obj), "https://www.rcsb.org/structure/1ABC")

        with override_settings(BASICLIVE_PUBLICATIONS={"PDB_URL_TEMPLATE": "https://pdb.example.com/{}/view"}):
            self.assertEqual(view.get_link_url(mock_obj), "https://pdb.example.com/1ABC/view")

        self.assertEqual(view.get_link_url(mock_obj), "https://www.rcsb.org/structure/1ABC")


class CrmConfTests(SimpleTestCase):
    def test_default_settings(self):
        self.assertEqual(dict(crm_settings), {})

    def test_crm_views_use_schedule_resolution(self):
        # Default in lims_settings is True
        self.assertIs(lims_settings.USE_SCHEDULE, True)

        with override_settings(BASICLIVE_LIMS={"USE_SCHEDULE": False}):
            self.assertIs(lims_settings.USE_SCHEDULE, False)

        self.assertIs(lims_settings.USE_SCHEDULE, True)


if __name__ == "__main__":
    unittest.main()
