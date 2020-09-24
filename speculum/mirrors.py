"""Mirror handling."""

from datetime import datetime
from json import load
from typing import Iterable
from urllib.parse import urlparse, ParseResult
from urllib.request import urlopen

from speculum.config import Configuration
from speculum.logging import LOGGER
from speculum.parsers import parse_datetime


__all__ = ['get_mirrors', 'get_lines']


MIRRORS_URL = 'https://www.archlinux.org/mirrors/status/json/'
REPO_PATH = '$repo/os/$arch'


def prepare_mirrors(mirrors: Iterable[dict]) -> Iterable[dict]:
    """Sets ages on mirrors."""

    now = datetime.now()

    for mirror in mirrors:
        if not mirror.get('url'):
            LOGGER.warning('Skipping mirror without URL.')
            continue

        if last_sync := mirror.get('last_sync'):
            last_sync = parse_datetime(last_sync)
        else:
            last_sync = datetime.fromtimestamp(0)

        mirror['age'] = now - last_sync
        yield mirror


def get_mirrors() -> Iterable[dict]:
    """Returns the mirrors from the respective URL."""

    with urlopen(MIRRORS_URL) as response:
        json = load(response)

    return prepare_mirrors(json['urls'])


def mirror_url(url: str) -> str:
    """Returns a mirror list URL."""

    scheme, netloc, path, params, query, fragment = urlparse(url)

    if not path.endswith('/'):
        path += '/'

    path += REPO_PATH
    url = ParseResult(scheme, netloc, path, params, query, fragment)
    return url.geturl()


def get_lines(mirrors: Iterable[dict], config: Configuration) -> Iterable[str]:
    """Returns a mirror list record."""

    if config.header:
        yield '# Mirror list generated with speculum'
        yield f'#     on {datetime.now()}'
        yield f'#     with configuration: {config}'

    for mirror in mirrors:
        url = mirror_url(mirror['url'])
        yield f'Server = {url}'
