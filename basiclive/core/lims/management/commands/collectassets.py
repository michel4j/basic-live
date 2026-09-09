# Modified from https://github.com/jochenklar/django-vendor-files/
from __future__ import annotations

import base64
import hashlib
import json

import requests
from urllib.parse import urljoin
from pathlib import Path
from django.apps import apps as django_apps, apps
from django.core.management.base import BaseCommand

from django.conf import settings


ASSETS_ROOT = getattr(settings, "BASICLIVE_ASSETS_ROOT", settings.STATIC_ROOT / "assets")


def download_asset(src_url, path: Path | str, sri: str | None = None):
    """
    Download an asset from the given URL and save it to the given path and verify it's checksum
    if SRI is provided
    :param src_url: Source URL
    :param path: Target path to save the file
    :param sri: SRI string for verification
    """

    # if file exists, check SRI and only download if new
    download_pending = True
    if Path(path).exists() and sri:
        algorithm, file_hash = sri.split('-')
        h = hashlib.new(algorithm)
        with open(path, 'rb') as f:
            content = f.read()
            h.update(content)
            if base64.b64encode(h.digest()).decode() == file_hash:
                print(f'{path} is up to date!')
                download_pending = False

    if download_pending:
        # fetch the file from the url
        response = requests.get(src_url)
        response.raise_for_status()

        # check the integrity of the file if an SRI was supplied
        if sri is not None:
            algorithm, file_hash = sri.split('-')
            h = hashlib.new(algorithm)
            h.update(response.content)
            if base64.b64encode(h.digest()).decode() != file_hash:
                print(f'File integrity mismatch: {path}!!!')
                return

        # Save the file
        with open(path, 'wb') as f:
            print(f'{src_url} -> {path}')
            f.write(response.content)


class Command(BaseCommand):
    help = 'Fetches static asset files from CDNs defined in `assets.json` files found in app/static/app directories'

    def handle(self, *args, **options):
        apps = django_apps.get_app_configs()
        assets_root = ASSETS_ROOT
        for app in apps:
            asset_path = None
            # read spec file. Prefer 'assets.json' and fallback to 'vendor.json'
            for spec_file in ['assets.json', 'vendor.json']:
                asset_path = Path(app.path) / 'static' / app.label / spec_file
                if asset_path.exists():
                    break
            else:
                continue

            with open(asset_path, 'r') as f:
                assets = json.load(f)

            for key, asset_conf in assets.items():
                url = asset_conf.pop('url')
                for kind in [k for k in asset_conf.keys()]:
                    for asset in asset_conf[kind]:
                        # get the directory and the file_name
                        filename = asset.get('file', Path(asset['path']).name)
                        file_path = assets_root / key / kind / filename
                        file_path.parent.mkdir(parents=True, exist_ok=True)

                        # get the full url of the file
                        file_url = urljoin(url, asset['path'])
                        download_asset(file_url, file_path, sri=asset.get('sri'))

