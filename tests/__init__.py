import django
from django.conf import settings


def setup_django():
    if not settings.configured:
        settings.configure(
            SECRET_KEY="test-secret-key",
            INSTALLED_APPS=[
                "django.contrib.auth",
                "django.contrib.contenttypes",
                "django.contrib.sessions",
                "django.contrib.humanize",
                "crispy_forms",
                "crispy_bootstrap5",
                "crisp_modals",
                "basiclive.core.lims",
                "basiclive.core.schedule",
                "basiclive.core.acl",
                "basiclive.core.api",
                "basiclive.core.publications",
                "basiclive.core.crm",
                "basiclive.auth.ldap",
                "basiclive.auth.cas",
            ],
            AUTH_USER_MODEL="lims.Project",
            DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "APP_DIRS": True,
                }
            ],
            ROOT_URLCONF="basiclive.core.lims.urls",
            CRISPY_ALLOWED_TEMPLATE_PACKS="bootstrap5",
            CRISPY_TEMPLATE_PACK="bootstrap5",
            BASICLIVE_TESTAPP={
                "CUSTOM_OPTION": "from_configured",
            },
            BASICLIVE_LIMS={
                "DOWNLOAD_PROXY_URL": "http://test-server/download",
            },
        )
        django.setup()


setup_django()
