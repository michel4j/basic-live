from typing import Any
from django.conf import settings as django_settings


class AppSettings:
    """
    Dynamic configuration proxy for BasicLIVE applications.

    Resolves settings from a dictionary namespace in django.conf.settings
    (e.g., BASICLIVE_LIMS) with fallback to application defaults.
    Evaluates dynamically on each attribute access to ensure compatibility
    with Django's @override_settings in tests.
    """

    def __init__(self, prefix: str, defaults: dict[str, Any]):
        """
        :param prefix: The application prefix for the settings dictionary,
                       e.g. 'LIMS' for settings.BASICLIVE_LIMS.
                       Can also be passed as a full name like 'BASICLIVE_LIMS'.
        :param defaults: Dictionary of default setting names and values.
        """
        if not prefix.startswith("BASICLIVE_"):
            namespace = f"BASICLIVE_{prefix.upper()}"
        else:
            namespace = prefix.upper()

        object.__setattr__(self, "_namespace", namespace)
        object.__setattr__(self, "_defaults", dict(defaults))

    @property
    def namespace(self) -> str:
        return self._namespace

    @property
    def defaults(self) -> dict[str, Any]:
        return self._defaults

    def __getattr__(self, name: str) -> Any:
        if name not in self._defaults:
            raise AttributeError(f"Invalid setting '{name}' for '{self._namespace}'")

        user_settings = getattr(django_settings, self._namespace, None)
        if isinstance(user_settings, dict) and name in user_settings:
            return user_settings[name]

        return self._defaults[name]

    def __getitem__(self, name: str) -> Any:
        try:
            return getattr(self, name)
        except AttributeError as e:
            raise KeyError(str(e)) from e

    def get(self, name: str, default: Any = None) -> Any:
        try:
            return getattr(self, name)
        except AttributeError:
            return default

    def __contains__(self, name: str) -> bool:
        return name in self._defaults

    def __dir__(self):
        return sorted(set(super().__dir__()) | set(self._defaults.keys()))

    def __setattr__(self, name: str, value: Any):
        raise AttributeError(
            f"'{self.__class__.__name__}' object attributes are read-only. "
            f"Configure settings via django.conf.settings.{self._namespace} "
            f"or @override_settings."
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} namespace={self._namespace!r}>"
