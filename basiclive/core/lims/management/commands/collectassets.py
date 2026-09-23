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

from basiclive.core.lims.icons import get_icon_backend


def get_assets_root() -> Path:
    assets_root = getattr(settings, "BASICLIVE_ASSETS_ROOT", None)
    if assets_root:
        return Path(assets_root)
    static_root = getattr(settings, "STATIC_ROOT", None) or Path("static")
    return Path(static_root) / "assets"


ASSETS_ROOT = get_assets_root()


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
    help = 'Fetches static asset files from CDNs defined in `assets.json` files and the active icon backend'

    def process_assets(self, assets: dict, assets_root: Path):
        for key, asset_conf in assets.items():
            conf = dict(asset_conf)
            url = conf.pop('url', '')
            for kind in conf.keys():
                for asset in conf[kind]:
                    # get the directory and the file_name
                    filename = asset.get('file', Path(asset['path']).name)
                    file_path = assets_root / key / kind / filename
                    file_path.parent.mkdir(parents=True, exist_ok=True)

                    # get the full url of the file
                    file_url = urljoin(url, asset['path'])
                    download_asset(file_url, file_path, sri=asset.get('sri'))

    def handle(self, *args, **options):
        apps = django_apps.get_app_configs()
        assets_root = get_assets_root()
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

            self.process_assets(assets, assets_root)

        # Process assets from configured IconBackend and run post_collect hook
        backend = get_icon_backend()
        backend_assets = backend.get_assets()
        if backend_assets:
            self.process_assets(backend_assets, assets_root)
        backend.post_collect(assets_root)

