from basiclive.utils.conf import AppSettings

DEFAULTS = {
    "APP_NAME": "BasicLIVE",
    "SUPPORT_EMAIL": "support@lightsource.ca",
    "USE_SCHEDULE": True,
    "USE_ACL": True,
    "USE_CRM": True,
    "USE_PUBLICATIONS": True,
    "DOWNLOAD_PROXY_URL": "http://basiclive.core-data/download",
    "MAX_CONTAINER_DEPTH": 2,
    "RESTRICT_DOWNLOADS": False,
    "LOADER_SELECT_DURATION": 5 * 60,  # 5 minutes
    "RESTRUCTUREDTEXT_FILTER_SETTINGS": {},
    "SEND_EMAILS": False,
    "BASE_DIR": "/tmp",
}

settings = AppSettings("LIMS", DEFAULTS)
