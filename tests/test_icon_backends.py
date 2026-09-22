import unittest
from django.test import SimpleTestCase, override_settings

from tests import setup_django
setup_django()

from basiclive.core.lims.icons import (
    BaseIconBackend,
    ThemifyBackend,
    get_icon_backend,
)


class DummyIconBackend(BaseIconBackend):
    name = "dummy"

    def resolve_icon_name(self, icon: str) -> str:
        return f"dummy-{icon}"

    def get_css_classes(self, icon: str, size: str = None, extra_class: str = "") -> str:
        classes = ["dummy", self.resolve_icon_name(icon)]
        size_cls = self.format_size_class(size)
        if size_cls:
            classes.append(size_cls)
        if extra_class:
            classes.append(extra_class)
        return " ".join(classes)

    def get_stylesheet_urls(self) -> list[str]:
        return ["dummy/dummy.css"]


class IconBackendTests(SimpleTestCase):
    def test_default_backend_resolution(self):
        backend = get_icon_backend()
        self.assertIsInstance(backend, ThemifyBackend)
        self.assertEqual(backend.name, "themify")

    @override_settings(BASICLIVE_ICON_BACKEND="tests.test_icon_backends.DummyIconBackend")
    def test_custom_backend_setting(self):
        backend = get_icon_backend()
        self.assertIsInstance(backend, DummyIconBackend)
        self.assertEqual(backend.name, "dummy")
        self.assertEqual(backend.get_css_classes("test", size="lg"), "dummy dummy-test bl-icon-lg")

    def test_themify_get_css_classes_plain_icon(self):
        backend = ThemifyBackend()
        self.assertEqual(backend.get_css_classes("home"), "ti ti-home")
        self.assertEqual(backend.get_css_classes("calendar", size="md"), "ti ti-calendar bl-icon-md")
        self.assertEqual(
            backend.get_css_classes("alert", size="sm", extra_class="text-danger"),
            "ti ti-alert bl-icon-sm text-danger"
        )

    def test_themify_allowed_sizes(self):
        backend = ThemifyBackend()
        for size in ("xs", "sm", "md", "lg", "xl"):
            classes = backend.get_css_classes("star", size=size)
            self.assertEqual(classes, f"ti ti-star bl-icon-{size}")

    def test_themify_invalid_size_raises(self):
        backend = ThemifyBackend()
        with self.assertRaises(ValueError) as ctx:
            backend.get_css_classes("star", size="2x")
        self.assertIn("Invalid icon size '2x'", str(ctx.exception))

    def test_themify_empty_or_whitespace_icon(self):
        backend = ThemifyBackend()
        self.assertEqual(backend.get_css_classes(""), "")
        self.assertEqual(backend.get_css_classes("   "), "")

    def test_themify_stylesheet_urls(self):
        backend = ThemifyBackend()
        self.assertEqual(backend.get_stylesheet_urls(), ["themify-icons/css/themify-icons.css"])

    def test_themify_aliases(self):
        backend = ThemifyBackend()
        # Aliases ensure unified canonical names resolve correctly in Themify
        self.assertEqual(backend.resolve_icon_name("comments"), "ti-comments")
        self.assertEqual(backend.resolve_icon_name("edit"), "ti-pencil")
        self.assertEqual(backend.resolve_icon_name("delete"), "ti-trash")
        self.assertEqual(backend.resolve_icon_name("add"), "ti-plus")
        self.assertEqual(backend.resolve_icon_name("remove"), "ti-minus")

    def test_render_icon_helper(self):
        from basiclive.core.lims.icons import render_icon
        self.assertEqual(render_icon("home"), '<i class="ti ti-home"></i>')
        self.assertEqual(
            render_icon("download", size="md", extra_class="text-primary"),
            '<i class="ti ti-download bl-icon-md text-primary"></i>'
        )
        self.assertEqual(render_icon(""), "")

    def test_base_backend_abstract_methods(self):
        backend = BaseIconBackend()
        with self.assertRaises(NotImplementedError):
            backend.resolve_icon_name("home")
        with self.assertRaises(NotImplementedError):
            backend.get_css_classes("home")
        with self.assertRaises(NotImplementedError):
            backend.get_stylesheet_urls()
