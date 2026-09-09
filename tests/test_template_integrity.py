import inspect
from pathlib import Path
import unittest

from tests import setup_django
setup_django()

from django import forms
from django.apps import apps
from django.contrib.staticfiles import finders
from django.template.loader import get_template
from django.test import SimpleTestCase
from django.urls import URLPattern, URLResolver

from basiclive.core.lims.models import DataType, Project, RequestType
import basiclive.core.lims.views as lims_views
import basiclive.core.acl.views as acl_views
import basiclive.core.crm.views as crm_views
import basiclive.core.schedule.views as schedule_views
import basiclive.core.publications.views as pub_views
import basiclive.core.lims.urls as lims_urls
import basiclive.core.acl.urls as acl_urls
import basiclive.core.crm.urls as crm_urls
import basiclive.core.schedule.urls as schedule_urls
import basiclive.core.publications.urls as pub_urls


class TemplateIntegrityTests(SimpleTestCase):
    """Automated tests verifying template paths, loading, compilation, and rendering."""

    VIEW_MODULES = [
        lims_views,
        acl_views,
        crm_views,
        schedule_views,
        pub_views,
    ]

    URL_MODULES = [
        lims_urls,
        acl_urls,
        crm_urls,
        schedule_urls,
        pub_urls,
    ]

    def test_all_view_template_names_exist(self):
        """Verify that every view class with a template_name or tool_template attribute points to an existing template."""
        checked = 0
        for mod in self.VIEW_MODULES:
            for name, obj in inspect.getmembers(mod, inspect.isclass):
                if obj.__module__ == mod.__name__:
                    tname = getattr(obj, "template_name", None)
                    if tname:
                        with self.subTest(view=f"{mod.__name__}.{name}", template=tname):
                            tmpl = get_template(tname)
                            self.assertIsNotNone(tmpl)
                            checked += 1
                    tool_template = getattr(obj, "tool_template", None)
                    if tool_template:
                        with self.subTest(view=f"{mod.__name__}.{name}", tool_template=tool_template):
                            tmpl = get_template(tool_template)
                            self.assertIsNotNone(tmpl)
                            checked += 1

        self.assertGreater(checked, 60, "Expected at least 60 view templates to be validated")

    def test_url_pattern_template_overrides_exist(self):
        """Verify that template_name overrides passed in as_view(...) in URL patterns exist."""
        def extract_patterns(pattern_list):
            results = []
            for p in pattern_list:
                if isinstance(p, URLPattern):
                    initkwargs = getattr(p.callback, "view_initkwargs", {}) or getattr(p.callback, "initkwargs", {})
                    if "template_name" in initkwargs:
                        results.append((str(p.pattern), initkwargs["template_name"]))
                elif isinstance(p, URLResolver):
                    results.extend(extract_patterns(p.url_patterns))
            return results

        overrides = []
        for umod in self.URL_MODULES:
            overrides.extend(extract_patterns(umod.urlpatterns))

        self.assertGreater(len(overrides), 0, "Expected URL pattern template overrides to be found")
        for pattern_str, tname in overrides:
            with self.subTest(pattern=pattern_str, template=tname):
                tmpl = get_template(tname)
                self.assertIsNotNone(tmpl)

    def test_data_detail_get_template_names(self):
        """Verify DataDetail.get_template_names() dynamically builds valid template candidates."""
        view = lims_views.DataDetail()
        kind = DataType(name="MX Dataset", acronym="DATA", template="lims/data/data-frames.html")
        view.object = type("DummyData", (), {"kind": kind})()

        names = view.get_template_names()
        self.assertEqual(names, ["lims/data/data-frames.html", "lims/data/data.html"])

        for tname in names:
            with self.subTest(template=tname):
                tmpl = get_template(tname)
                self.assertIsNotNone(tmpl)

    def test_request_type_template_defaults(self):
        """Verify RequestType model template path defaults and standard request templates."""
        edit_default = RequestType._meta.get_field("edit_template").default
        self.assertEqual(edit_default, "lims/requests/base-edit.html")
        self.assertIsNotNone(get_template(edit_default))

        standard_request_templates = [
            "lims/requests/base-edit.html",
            "lims/requests/base-view.html",
            "lims/requests/exafs-edit.html",
            "lims/requests/exafs-view.html",
            "lims/requests/imgir-edit.html",
            "lims/requests/imgir-view.html",
        ]
        for tname in standard_request_templates:
            with self.subTest(template=tname):
                tmpl = get_template(tname)
                self.assertIsNotNone(tmpl)

    def test_data_type_templates(self):
        """Verify standard DataType templates exist and load."""
        standard_data_templates = [
            "lims/data/data.html",
            "lims/data/data-frames.html",
            "lims/data/data-mad.html",
            "lims/data/data-xrf.html",
        ]
        for tname in standard_data_templates:
            with self.subTest(template=tname):
                tmpl = get_template(tname)
                self.assertIsNotNone(tmpl)

    def test_templatetag_and_component_templates_exist(self):
        """Verify component and inclusion tag templates exist."""
        component_templates = [
            "lims/components/badge-score.html",
            "lims/components/badge-label.html",
            "lims/components/icon-info.html",
            "lims/guides.html",
            "lims/comments.html",
            "lims/messages.html",
            "lims/navs.html",
            "crm/forms/likert-table.html",
            "crm/forms/likert-entry.html",
            "acl/tools-access.html",
            "crm/tools-support.html",
            "lims/tools-base.html",
            "lims/tools-shipment.html",
            "lims/tools-shipment-edit.html",
            "lims/tools-user.html",
            "publications/tools.html",
        ]
        for tname in component_templates:
            with self.subTest(template=tname):
                tmpl = get_template(tname)
                self.assertIsNotNone(tmpl)

    def test_all_app_templates_load_and_compile(self):
        """Verify every HTML template file across all core apps loads and compiles without syntax error."""
        app_names = [
            "basiclive.core.lims",
            "basiclive.core.acl",
            "basiclive.core.crm",
            "basiclive.core.schedule",
            "basiclive.core.publications",
        ]
        loaded_count = 0
        for app_name in app_names:
            app_config = apps.get_app_config(app_name.split(".")[-1])
            template_dir = Path(app_config.path) / "templates"
            if not template_dir.is_dir():
                continue

            for html_file in template_dir.rglob("*.html"):
                rel_path = str(html_file.relative_to(template_dir))
                with self.subTest(app=app_name, template=rel_path):
                    tmpl = get_template(rel_path)
                    self.assertIsNotNone(tmpl)
                    loaded_count += 1

        self.assertGreater(loaded_count, 60, "Expected at least 60 templates on disk across apps")

    def test_error_handlers_render(self):
        """Verify error handler templates (403, 403_csrf, 404, 500) exist and render."""
        error_templates = [
            ("403.html", {"reason": "Permission denied"}),
            ("403_csrf.html", {"reason": "CSRF verification failed"}),
            ("404.html", {"request_path": "/missing/path/"}),
            ("500.html", {}),
        ]
        for tname, ctx in error_templates:
            with self.subTest(template=tname):
                tmpl = get_template(tname)
                rendered = tmpl.render(ctx)
                self.assertIsInstance(rendered, str)
                self.assertGreater(len(rendered.strip()), 0)

    def test_core_layout_and_modal_templates_render(self):
        """Verify core base layout and modal wrapper templates render properly."""
        class DummyForm(forms.Form):
            name = forms.CharField()

        class DummyWizard:
            steps = type("Steps", (), {"step0": 0, "step1": 1, "count": 2, "prev": None, "next": "step2"})()
            form = DummyForm()

        project = Project(username="testuser", name="Test User")

        cases = [
            ("lims/base.html", {"user": None}),
            ("lims/modal/content.html", {"title": "Test Title"}),
            ("lims/modal/form.html", {"form": DummyForm(), "title": "Edit Item"}),
            ("lims/modal/delete.html", {"object": project, "title": "Delete Item"}),
            ("lims/modal/wizard.html", {"wizard": DummyWizard(), "title": "New Item"}),
        ]
        for tname, ctx in cases:
            with self.subTest(template=tname):
                tmpl = get_template(tname)
                rendered = tmpl.render(ctx)
                self.assertIsInstance(rendered, str)
                self.assertGreater(len(rendered.strip()), 0)

    def test_basiclive_static_assets_exist(self):
        """Verify that all renamed BasicLIVE static assets exist and old mxlive assets do not."""
        expected_assets = [
            "lims/css/basiclive.scss",
            "lims/css/basiclive.min.css",
            "lims/css/basiclive.min.css.map",
            "lims/js/basiclive-diffviewer.js",
            "lims/js/basiclive-diffviewer.min.js",
            "lims/js/basiclive-forms.js",
            "lims/js/basiclive-forms.min.js",
            "lims/js/basiclive-layouts.js",
            "lims/js/basiclive-layouts.min.js",
            "lims/js/basiclive-modals.js",
            "lims/js/basiclive-modals.min.js",
            "lims/js/basiclive-reports.js",
            "lims/js/basiclive-reports.min.js",
            "lims/js/basiclive-seater.js",
            "lims/js/basiclive-seater.min.js",
            "lims/js/basiclive-spreadsheet.js",
            "lims/js/basiclive-spreadsheet.min.js",
            "schedule/js/basiclive-scheduler.js",
        ]
        for asset in expected_assets:
            with self.subTest(asset=asset):
                path = finders.find(asset)
                self.assertIsNotNone(path, f"Expected static asset not found: {asset}")

        obsolete_assets = [
            "lims/css/mxlive.scss",
            "lims/css/mxlive.min.css",
            "lims/css/mxlive.min.css.map",
            "lims/js/mxlive-diffviewer.js",
            "lims/js/mxlive-diffviewer.min.js",
            "lims/js/mxlive-forms.js",
            "lims/js/mxlive-forms.min.js",
            "lims/js/mxlive-layouts.js",
            "lims/js/mxlive-layouts.min.js",
            "lims/js/mxlive-modals.js",
            "lims/js/mxlive-modals.min.js",
            "lims/js/mxlive-reports.js",
            "lims/js/mxlive-reports.min.js",
            "lims/js/mxlive-seater.js",
            "lims/js/mxlive-seater.min.js",
            "lims/js/mxlive-spreadsheet.js",
            "lims/js/mxlive-spreadsheet.min.js",
            "schedule/js/mxlive-scheduler.js",
        ]
        for asset in obsolete_assets:
            with self.subTest(obsolete_asset=asset):
                path = finders.find(asset)
                self.assertIsNone(path, f"Obsolete mxlive asset still found: {asset}")

    def test_rendered_templates_use_basiclive_assets(self):
        """Verify key rendered templates output basiclive asset URLs and no mxlive asset URLs."""
        class DummyForm(forms.Form):
            name = forms.CharField()

        class DummyWizard:
            steps = type("Steps", (), {"step0": 0, "step1": 1, "count": 2, "prev": None, "next": "step2"})()
            form = DummyForm()

        base_tmpl = get_template("lims/base.html")
        rendered_base = base_tmpl.render({"user": None})
        self.assertIn("bootstrap/css/bootstrap.min.css", rendered_base)
        self.assertIn("lims/css/basiclive.min.css", rendered_base)
        self.assertIn("lims/js/basiclive-modals.min.js", rendered_base)
        self.assertNotIn("mxlive", rendered_base.lower())

        wizard_tmpl = get_template("lims/modal/wizard.html")
        rendered_wizard = wizard_tmpl.render({"wizard": DummyWizard(), "title": "New Item"})
        self.assertIn("lims/js/basiclive-forms.min.js", rendered_wizard)
        self.assertNotIn("mxlive", rendered_wizard.lower())

        schedule_tmpl = get_template("schedule/schedule.html")
        self.assertIn("schedule/js/basiclive-scheduler.js", schedule_tmpl.template.source)
        self.assertNotIn("mxlive", schedule_tmpl.template.source.lower())

    def test_no_mxlive_references_in_any_template(self):
        """Verify that no HTML template across any core app contains references to mxlive."""
        app_names = [
            "basiclive.core.lims",
            "basiclive.core.acl",
            "basiclive.core.crm",
            "basiclive.core.schedule",
            "basiclive.core.publications",
        ]
        for app_name in app_names:
            app_config = apps.get_app_config(app_name.split(".")[-1])
            template_dir = Path(app_config.path) / "templates"
            if not template_dir.is_dir():
                continue

            for html_file in template_dir.rglob("*.html"):
                content = html_file.read_text(encoding="utf-8")
                rel_path = str(html_file.relative_to(template_dir))
                with self.subTest(app=app_name, template=rel_path):
                    self.assertNotIn("mxlive", content.lower(), f"Found 'mxlive' reference in {app_name}/{rel_path}")

    def test_crispy_bootstrap5_configuration_and_rendering(self):
        """Verify crispy_forms is configured with crispy_bootstrap5 and renders Bootstrap 5 form markup."""
        from django.conf import settings
        from crispy_forms.helper import FormHelper
        from django.template import Context, Template

        self.assertIn("crispy_bootstrap5", settings.INSTALLED_APPS)
        self.assertEqual(getattr(settings, "CRISPY_TEMPLATE_PACK", None), "bootstrap5")

        class SampleForm(forms.Form):
            title = forms.CharField(label="Title")

        form = SampleForm()
        form.helper = FormHelper()
        form.helper.form_tag = False
        template = Template("{% load crispy_forms_tags %}{% crispy form %}")
        rendered = template.render(Context({"form": form}))

        # Bootstrap 5 crispy forms uses 'mb-3' and 'form-label' rather than BS4 'form-group'
        self.assertIn("mb-3", rendered)
        self.assertIn("form-label", rendered)
        self.assertIn("form-control", rendered)
        self.assertNotIn("form-group", rendered)

    def test_bootstrap5_and_select2_theme_assets(self):
        """Verify assets.json and templates use Bootstrap 5 and select2-bootstrap-5-theme."""
        import json
        assets_file = Path(apps.get_app_config("lims").path) / "static" / "lims" / "assets.json"
        self.assertTrue(assets_file.exists())
        with open(assets_file, "r") as f:
            assets_data = json.load(f)

        # Bootstrap 5 assets
        bootstrap_conf = assets_data.get("bootstrap", {})
        self.assertIn("bootstrap@5", bootstrap_conf.get("url", ""))
        css_paths = [entry["path"] for entry in bootstrap_conf.get("css", [])]
        js_paths = [entry["path"] for entry in bootstrap_conf.get("js", [])]
        self.assertIn("css/bootstrap.min.css", css_paths)
        self.assertIn("js/bootstrap.bundle.min.js", js_paths)

        # Select2 Bootstrap 5 theme
        misc_css = [entry["path"] for entry in assets_data.get("misc", {}).get("css", [])]
        self.assertTrue(any("select2-bootstrap-5-theme" in p for p in misc_css))
        self.assertFalse(any("select2-bootstrap4" in p for p in misc_css))

        # Template references
        req_tmpl = get_template("lims/details/requesttype.html")
        self.assertIn("select2-bootstrap-5-theme.min.css", req_tmpl.template.source)
        self.assertNotIn("select2-bootstrap4", req_tmpl.template.source)

        modal_tmpl = get_template("lims/modal/form.html")
        self.assertIn("select2-bootstrap-5-theme.min.css", modal_tmpl.template.source)
        self.assertNotIn("select2-bootstrap4", modal_tmpl.template.source)

    def test_vendored_bootstrap_scss_removed_and_css_variables_configured(self):
        """Verify vendored Bootstrap SCSS is removed and basiclive.scss overrides CSS custom properties."""
        lims_static = Path(apps.get_app_config("lims").path) / "static"
        vendored_scss_dir = lims_static / "bootstrap" / "scss"
        self.assertFalse(vendored_scss_dir.exists(), "Vendored Bootstrap SCSS directory should be removed")

        scss_file = lims_static / "lims" / "css" / "basiclive.scss"
        self.assertTrue(scss_file.exists())
        scss_content = scss_file.read_text(encoding="utf-8")

        self.assertNotIn("@import \"../../bootstrap/scss/bootstrap\";", scss_content)
        self.assertIn("--bs-primary", scss_content)
        self.assertIn("--bs-border-color", scss_content)


if __name__ == "__main__":
    unittest.main()
