from basiclive.utils.conf import AppSettings

DEFAULTS = {
    "TRUSTED_IPS": ["127.0.0.1/32"],
    "TRUSTED_URLS": ['^/json', '^/api'],
    "TRUSTED_PROXIES": 2,
}

settings = AppSettings("ACL", DEFAULTS)
