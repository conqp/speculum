"""Mirror filtering implementation for the original Arch Linux."""

from functools import partial
from logging import DEBUG, INFO, basicConfig
from typing import Iterable
from urllib.error import URLError

from speculum.argparse import parse_args
from speculum.cli import iterprint
from speculum.config import Configuration
from speculum.fileio import dump_mirrors
from speculum.filtering import match
from speculum.limiting import limit
from speculum.logging import LOG_FORMAT, LOGGER
from speculum.mirrors import get_mirrors, get_lines
from speculum.sorting import get_sorting_key


__all__ = ['main']


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


def list_countries(mirrors: Iterable[dict], reverse: bool = False) -> int:
    """Lists available countries."""

    countries = {(mirr['country'], mirr['country_code']) for mirr in mirrors}
    countries = filter(lambda country: country[0] and country[1], countries)
    countries = sorted(countries, reverse=reverse)
    iterprint(f'{name} ({code})' for name, code in countries)
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

    lines = get_lines(mirrors, config)

    if config.output:
        LOGGER.debug('Writing mirror list to "%s".', config.output)
        return 0 if dump_mirrors(lines, config.output) else 1

    iterprint(lines)
    return 0
