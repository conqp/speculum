"""Mirror list optimization CLI utility for Arch Linux."""

from functools import partial
from logging import DEBUG, INFO, basicConfig
from urllib.error import HTTPError, URLError

from speculum.argparse import parse_args
from speculum.config import Configuration
from speculum.io import dump_mirrors, exiting, iterprint
from speculum.filtering import get_filters, match
from speculum.limiting import limit
from speculum.logging import LOG_FORMAT, LOGGER
from speculum.mirrors import SORTING_DEFAULTS
from speculum.mirrors import get_mirrors
from speculum.mirrors import get_lines
from speculum.mirrors import list_countries
from speculum.sorting import get_sorting_key


__all__ = ['main']


@exiting
def main() -> int:
    """Filters and sorts the mirrors."""

    args = parse_args()
    basicConfig(level=DEBUG if args.verbose else INFO, format=LOG_FORMAT)
    config = Configuration.load(args)

    if args.list_sortopts:
        iterprint(sorted(SORTING_DEFAULTS.keys(), reverse=config.reverse))
        return 0

    try:
        mirrors = get_mirrors()
    except (HTTPError, URLError) as err:
        LOGGER.error('Could not download mirror list.')
        LOGGER.debug(err)
        return 2

    if args.list_countries:
        list_countries(mirrors, reverse=config.reverse)
        return 0

    LOGGER.debug('Filtering mirrors.')
    filters = set(get_filters(config))
    mirrors = filter(partial(match, filters), mirrors)

    if config.sort:
        LOGGER.debug('Sorting mirrors.')
        key = get_sorting_key(config.sort, SORTING_DEFAULTS)
        mirrors = sorted(mirrors, key=key, reverse=config.reverse)

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
        return 0 if dump_mirrors(lines, config.output) else 3

    iterprint(lines)
    return 0
