"""
Pluggable icon subsystem for BasicLIVE.

Provides backend-agnostic icon resolution, sizing classes, and stylesheet injection.
"""

from typing import List, Optional

from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe


class BaseIconBackend:
    """
    Abstract base class for BasicLIVE icon backends.
    """
    name = "base"
    allowed_sizes = ("xs", "sm", "md", "lg", "xl")
    size_class_prefix = "bl-icon-"

    def format_size_class(self, size: Optional[str] = None) -> str:
        """
        Validates and returns the CSS class corresponding to a standardized size literal.
        """
        if not size:
            return ""
        size_str = str(size).strip().lower()
        if size_str not in self.allowed_sizes:
            raise ValueError(
                f"Invalid icon size '{size}'. Allowed sizes: {', '.join(self.allowed_sizes)}"
            )
        return f"{self.size_class_prefix}{size_str}"

    def resolve_icon_name(self, icon: str) -> str:
        """
        Resolves a canonical icon name into the provider-specific icon class.
        """
        raise NotImplementedError("Icon backends must implement resolve_icon_name()")

    def get_css_classes(
        self,
        icon: str,
        size: Optional[str] = None,
        extra_class: str = ""
    ) -> str:
        """
        Returns the full combined CSS class string for rendering the icon.
        """
        raise NotImplementedError("Icon backends must implement get_css_classes()")

    def get_stylesheet_urls(self) -> List[str]:
        """
        Returns a list of static asset relative paths or URLs required for this icon font.
        """
        raise NotImplementedError("Icon backends must implement get_stylesheet_urls()")


class ThemifyBackend(BaseIconBackend):
    """
    Default icon backend using Themify Icons.
    """
    name = "themify"
    base_class = "ti"
    icon_prefix = "ti-"
    stylesheet_urls = ("themify-icons/css/themify-icons.css",)

    # Canonical aliases mapping semantic action/object names to Themify glyph names
    aliases = {
        "add": "plus",
        "remove": "minus",
        "edit": "pencil",
        "delete": "trash",
        "view": "eye",
        "history": "timer",
        "stats": "pulse",
        "usage": "pie-chart",
        "connections": "rss-alt",
        "feedback": "star",
        "support": "headphone-alt",
        "areas": "target",
        "new-area": "target",
        "request": "ruler-pencil",
        "samples": "paint-bucket",
        "profile": "user",
        'journal': 'agenda',
        "projects": "briefcase",
        'help': 'help-alt',
        'text-entry': 'align-left',
        'file-entry': 'clip',
        'image-entry': 'image',
        'video-entry': 'youtube',
        'sketch-entry': 'brush',
        'data-entry': 'layout-grid3',
    }

    def resolve_icon_name(self, icon: str) -> str:
        clean = icon.strip()
        if not clean:
            return ""
        # Support plain names, ti-prefixed names, and legacy compound strings
        tokens = clean.split()
        canonical = tokens[-1]
        for token in tokens:
            if token.startswith("ti-") and token not in ("ti-xs", "ti-sm", "ti-md", "ti-lg", "ti-xl"):
                canonical = token
                break
        if canonical.startswith("ti-"):
            canonical = canonical[3:]
        target = self.aliases.get(canonical, canonical)
        if target.startswith("entry-selector-"):
            return target
        return f"{self.icon_prefix}{target}"

    def get_css_classes(
        self,
        icon: str,
        size: Optional[str] = None,
        extra_class: str = ""
    ) -> str:
        if not icon or not icon.strip():
            return ""

        clean = icon.strip()
        # Fallback to extract size token from legacy compound string if size argument omitted
        if not size:
            for token in clean.split():
                if token.startswith("ti-") and token[3:] in self.allowed_sizes:
                    size = token[3:]
                    break

        parts = [self.base_class, self.resolve_icon_name(icon)]
        size_cls = self.format_size_class(size)
        if size_cls:
            parts.append(size_cls)
        if extra_class and extra_class.strip():
            parts.append(extra_class.strip())
        return " ".join(parts)

    def get_stylesheet_urls(self) -> List[str]:
        return list(self.stylesheet_urls)


def get_icon_backend() -> BaseIconBackend:
    """
    Retrieves the configured icon backend instance.
    Defaults to ThemifyBackend.
    """
    backend_config = getattr(
        settings,
        "BASICLIVE_ICON_BACKEND",
        "basiclive.core.lims.icons.ThemifyBackend"
    )

    if isinstance(backend_config, BaseIconBackend):
        return backend_config
    if isinstance(backend_config, type) and issubclass(backend_config, BaseIconBackend):
        return backend_config()
    if isinstance(backend_config, str):
        backend_cls = import_string(backend_config)
        return backend_cls()

    raise ValueError(
        f"Invalid BASICLIVE_ICON_BACKEND: {backend_config!r}. Expected a subclass or dotted path to BaseIconBackend."
    )


def render_icon(
    icon: Optional[str] = None,
    size: Optional[str] = None,
    extra_class: Optional[str] = None,
    name: Optional[str] = None,
) -> str:
    """
    Convenience helper to render a standalone HTML icon element for use in Python code (forms, admin).
    Accepts either 'icon' or 'name' as positional or keyword argument.
    """
    icon_name = name or icon
    if not icon_name or not str(icon_name).strip():
        return mark_safe("")
    classes = get_icon_backend().get_css_classes(str(icon_name), size=size, extra_class=extra_class or "")
    if not classes:
        return mark_safe("")
    return mark_safe(f'<i class="{classes}"></i>')
