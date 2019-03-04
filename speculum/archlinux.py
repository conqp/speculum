"""Mirror filtering implementation for the original Arch Linux."""

from datetime import datetime
from functools import partial
from json import load
from logging import DEBUG, WARNING, basicConfig
from os import linesep
from pathlib import Path
from typing import Iterable
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import urlopen

from speculum.argparse import parse_args
from speculum.cli import iterprint
from speculum.filtering import match
from speculum.limiting import limit
from speculum.logging import LOGGER, LOG_FORMAT
from speculum.parsers import parse_datetime
from speculum.sorting import get_sorting_key


__all__ = ['main']


MIRRORS_URL = 'https://www.archlinux.org/mirrors/status/json/'
REPO_PATH = '$repo/os/$arch'
SORTING_DEFAULTS = {
    'url': '',
    'protocol': '~',
    'last_sync': '~',
    'completion_pct': 0,
    'delay': float('inf'),
    'duration_avg': float('inf'),
    'duration_stddev': float('inf'),
    'score': float('inf'),
    'country': '~',
    'country_code': '~',
    'age': None
}


def set_ages(mirrors: list) -> list:
    """Sets ages on mirrors."""

    now = datetime.now()

    for mirror in mirrors:
        last_sync = mirror.get('last_sync')

        if last_sync:
            last_sync = parse_datetime(last_sync)
        else:
            last_sync = datetime.fromtimestamp(0)

        mirror['age'] = now - last_sync

    return mirrors


def get_mirrors(url: str = MIRRORS_URL) -> list:
    """Returns the mirrors from the respective URL."""

    with urlopen(url) as response:
        json = load(response)

    return set_ages(json['urls'])


def mirror_url(url: str) -> str:
    """Returns a mirror list URL."""

    if not url.endswith('/'):
        url += '/'

    return urljoin(url, REPO_PATH)


def get_mirrorlist(mirrors: Iterable[dict]) -> Iterable[str]:
    """Returns a mirror list record."""

    for mirror in mirrors:
        url = mirror['url']

        if not url:
            LOGGER.warning('Skipping mirror without URL.')
            continue

        url = mirror_url(url)
        yield f'Server = {url}'


def list_countries(mirrors: Iterable[dict], reverse: bool = False) -> int:
    """Lists available countries."""

    countries = ((mirr['country'], mirr['country_code']) for mirr in mirrors)
    countries = filter(lambda country: country[0] and country[1], countries)
    countries = sorted(frozenset(countries), reverse=reverse)
    iterprint(f'{name} ({code})' for name, code in countries)
    return 0


def dump_mirrors(mirrors: list, path: Path) -> int:
    """Dumps the mirrors to the given path."""

    mirrorlist = linesep.join(get_mirrorlist(mirrors))

    try:
        with path.open('w') as file:
            file.write(mirrorlist + linesep)
    except PermissionError as permission_error:
        LOGGER.error(permission_error)
        return 1

    return 0


def main() -> int:
    """Filters and sorts the mirrors."""

    args = parse_args()
    basicConfig(level=DEBUG if args.verbose else WARNING, format=LOG_FORMAT)

    if args.list_sortopts:
        iterprint(sorted(SORTING_DEFAULTS.keys(), reverse=args.reverse))
        return 0

    try:
        mirrors = get_mirrors(url=args.url)
    except (ValueError, URLError) as err:
        LOGGER.error('Could not download mirror list.')
        LOGGER.debug(err)
        return 1

    LOGGER.info('Received %i mirrors.', len(mirrors))

    if args.list_countries:
        return list_countries(mirrors, reverse=args.reverse)

    mirrors = filter(partial(match, args), mirrors)

    if args.sort:
        key = get_sorting_key(args.sort, SORTING_DEFAULTS)
        mirrors = sorted(mirrors, key=key, reverse=args.reverse)

    if args.limit:
        mirrors = limit(mirrors, args.limit)

    mirrors = tuple(mirrors)

    if not mirrors and args.limit != 0:
        LOGGER.error('No mirrors found.')
        return 1

    if args.limit is not None and len(mirrors) < args.limit:
        LOGGER.warning('Filter yielded less mirrors than specified limit.')

    if args.output:
        return dump_mirrors(mirrors, args.output)

    iterprint(get_mirrorlist(mirrors))
    return 0
