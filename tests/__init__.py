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
                "basiclive.core.lims",
            ],
            AUTH_USER_MODEL="lims.Project",
            DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "APP_DIRS": True,
                }
            ],
            BASICLIVE_TESTAPP={
                "CUSTOM_OPTION": "from_configured",
            },
            BASICLIVE_LIMS={
                "DOWNLOAD_PROXY_URL": "http://test-server/download",
            },
        )
        django.setup()


setup_django()
