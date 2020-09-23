"""Mirror filtering implementation for the original Arch Linux."""

from datetime import datetime
from functools import partial
from json import load
from logging import DEBUG, INFO, basicConfig
from os import linesep
from pathlib import Path
from typing import Iterable
from urllib.error import URLError
from urllib.parse import urlparse, ParseResult
from urllib.request import urlopen

from speculum.argparse import parse_args
from speculum.cli import iterprint
from speculum.config import Configuration
from speculum.filtering import match
from speculum.limiting import limit
from speculum.logging import LOG_FORMAT, LOGGER
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
        if last_sync := mirror.get('last_sync'):
            last_sync = parse_datetime(last_sync)
        else:
            last_sync = datetime.fromtimestamp(0)

        mirror['age'] = now - last_sync

    return mirrors


def get_mirrors() -> list:
    """Returns the mirrors from the respective URL."""

    with urlopen(MIRRORS_URL) as response:
        json = load(response)

    return set_ages(json['urls'])


def mirror_url(url: str) -> str:
    """Returns a mirror list URL."""

    scheme, netloc, path, params, query, fragment = urlparse(url)

    if not path.endswith('/'):
        path += '/'

    path += REPO_PATH
    url = ParseResult(scheme, netloc, path, params, query, fragment)
    return url.geturl()


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

    countries = {(mirr['country'], mirr['country_code']) for mirr in mirrors}
    countries = filter(lambda country: country[0] and country[1], countries)
    countries = sorted(countries, reverse=reverse)
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
    basicConfig(level=DEBUG if args.verbose else INFO, format=LOG_FORMAT)

    if args.list_sortopts:
        iterprint(sorted(SORTING_DEFAULTS.keys(), reverse=args.reverse))
        return 0

    try:
        mirrors = get_mirrors()
    except (ValueError, URLError) as err:
        LOGGER.error('Could not download mirror list.')
        LOGGER.debug(err)
        return 1

    LOGGER.debug('Received %i available mirrors.', len(mirrors))

    if args.list_countries:
        return list_countries(mirrors, reverse=args.reverse)

    config = Configuration.load(args)
    LOGGER.debug('Filtering mirrors.')
    mirrors = filter(partial(match, config), mirrors)

    if config.sort:
        LOGGER.debug('Sorting mirrors.')
        key = get_sorting_key(config.sort, SORTING_DEFAULTS)
        mirrors = sorted(mirrors, key=key, reverse=args.reverse)

    if config.limit:
        LOGGER.debug('Limiting mirrors.')
        mirrors = limit(mirrors, config.limit)

    mirrors = tuple(mirrors)

    if not mirrors and config.limit != 0:
        LOGGER.error('No mirrors found.')
        return 1

    mirror_count = len(mirrors)
    LOGGER.info('Mirror list contains %i mirrors.', mirror_count)

    if config.limit is not None and mirror_count < config.limit:
        LOGGER.warning('Filter yielded less mirrors than specified limit.')

    if config.output:
        LOGGER.debug('Writing mirror list to "%s".', config.output)
        return dump_mirrors(mirrors, config.output)

    iterprint(get_mirrorlist(mirrors))
    return 0
