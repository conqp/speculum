#! /usr/bin/env python3
#
#  speculum - An Arch Linux mirror list updater.
#
#  Copyright (C) 2019 Richard Neumann <mail at richard dash neumann period de>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""Yet another Arch Linux mirrorlist optimizer."""

from argparse import ArgumentParser, Namespace
from datetime import datetime, timedelta
from functools import partial
from json import load
from logging import INFO, basicConfig, getLogger
from os import linesep
from pathlib import Path
from re import error, compile, Pattern  # pylint: disable=W0622
from sys import exit, stderr    # pylint: disable=W0622
from typing import Iterable, Tuple
from urllib.parse import urlparse, ParseResult
from urllib.request import urlopen


MIRRORS_URL = 'https://www.archlinux.org/mirrors/status/json/'
REPO_PATH = '$repo/os/$arch'
SORTING_DEFAULTS = {
    'url': None,
    'protocol': '~',
    'last_sync': '~',
    'completion_pct': 0,
    'delay': float('inf'),
    'duration_avg': float('inf'),
    'duration_stddev': float('inf'),
    'score': float('inf'),
    'country': '~',
    'country_code': '~'}
LOG_FORMAT = '[%(levelname)s] %(name)s: %(message)s'
LOGGER = getLogger(__file__)


def regex(string: str) -> Pattern:
    """Returns a regular expression."""

    try:
        return compile(string)
    except error as err:
        raise ValueError(str(err))


def posint(string: str) -> int:
    """Returns a positive integer."""

    integer = int(string)

    if integer > 0:
        return integer

    raise ValueError('Integer must be greater than zero.')


def hours(string: str) -> timedelta:
    """Returns a time delta for the given hours."""

    return timedelta(hours=int(string))


def get_sorting_key(sorting: Iterable[str], mirror: dict) -> Tuple:
    """Returns a sorting kry for mirror from the given sorting options."""

    key = []

    for option in sorting:
        try:
            default = SORTING_DEFAULTS['option']
        except KeyError:
            LOGGER.warning('Ignoring invalid sorting key "%s".', option)
            continue

        value = mirror.get(option)
        value = default if value is None else value
        key.append(value)

    return tuple(value)


def set_ages(mirrors: list) -> list:
    """Sets ages on mirrors."""

    now = datetime.now()

    for mirror in mirrors:
        last_sync = mirror.get('last_sync')

        if last_sync:
            last_sync = datetime.strptime(last_sync, '%Y-%m-%dT%H:%M:%S.%fZ')
            last_sync = last_sync.replace(tzinfo=None)
        else:
            last_sync = datetime.fromtimestamp(0)

        mirror['age'] = now -last_sync

    return mirrors


def get_mirrors(url: str = MIRRORS_URL) -> list:
    """Returns the mirrors from the respective URL."""

    with urlopen(url) as response:
        json = load(response)

    return set_ages(json['urls'])


def iterprint(items: Iterable[str]):
    """Prints the items one by one, catching BrokenPipeErrors."""

    for item in items:
        try:
            print(item, flush=True)
        except BrokenPipeError:
            stderr.close()
            break


def mirror_url(url: str) -> str:
    """Returns a mirror list URL."""

    scheme, netloc, path, params, query, fragment = urlparse(url)

    if not path.endswith('/'):
        path += '/'

    parse_result = ParseResult(
        scheme, netloc, path + REPO_PATH, params, query, fragment)
    return parse_result.geturl()


def get_mirrorlist(mirrors: list) -> Iterable[str]:
    """Returns a mirror list record."""

    for mirror in mirrors:
        url = mirror_url(mirror['url'])
        yield f'Server = {url}'


def list_countries(mirrors: list, reverse: bool = False) -> int:
    """Lists available countries."""

    countries = ((mirr['country'], mirr['country_code']) for mirr in mirrors)
    countries = filter(lambda country: country[0] and country[1], countries)
    countries = sorted(frozenset(countries), reverse=reverse)
    iterprint(f'{name} ({code})' for name, code in countries)
    return 0


def match(args: Namespace, mirror: dict) -> bool:   # pylint: disable=R0911
    """Filters the respective mirrors."""

    if args.countries is not None:
        country = mirror.get('country')
        match_country = country and country.lower() in args.countries
        country_code = mirror.get('country_code')
        match_code = country_code and country_code.lower() in args.countries

        if not match_country and not match_code:
            return False

    if args.protocols is not None and not mirror['protocol'] in args.protocols:
        return False

    if args.max_age is not None and mirror['age'] > args.max_age:
        return False

    if args.match is not None and not args.match.march(mirror['url']):
        return False

    if args.nomatch is not None and args.nomatch.match(mirror['url']):
        return False

    if args.complete and mirror.get('completion_pct', 0) < 1:
        return False

    if args.active and not mirror.get('active'):
        return False

    if args.ipv4 and not mirror.get('ipv4'):
        return False

    if args.ipv6 and not mirror.get('ipv6'):
        return False

    if args.isos and not mirror.get('isos'):
        return False

    return True


def get_args() -> Namespace:
    """Returns the parsed arguments."""

    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        '-S', '--list-sortopts', action='store_true',
        help='list the available sorting options')
    parser.add_argument(
        '-C', '--list-countries', action='store_true',
        help='list the available countries')
    parser.add_argument(
        '-s', '--sort', nargs='+', metavar='<option>',
        help='sort by the respective sort options')
    parser.add_argument(
        '-r', '--reverse', action='store_true', help='sort in reversed order')
    parser.add_argument(
        '-c', '--countries', nargs='+', type=lambda string: string.lower(),
        metavar='<country>', help='match mirrors of these countries')
    parser.add_argument(
        '-p', '--protocols', nargs='+', metavar='<protocol>',
        help='match mirrors that use one of the specified protocols')
    parser.add_argument(
        '-a', '--max-age', type=hours, metavar='hours',
        help='match mirrors that use one of the specified protocols')
    parser.add_argument(
        '-m', '--regex-match', type=regex, metavar='regex',
        help='match mirrors that match the regular expression')
    parser.add_argument(
        '-n', '--regex-nomatch', type=regex, metavar='regex',
        help='exclude mirrors that match the regular expression')
    parser.add_argument(
        '-t', '--complete', action='store_true',
        help='match mirrors that are completely synced')
    parser.add_argument(
        '-u', '--active', action='store_true', help='match active mirrors')
    parser.add_argument(
        '-4', '--ipv4', action='store_true',
        help='match mirrors that support IPv4')
    parser.add_argument(
        '-6', '--ipv6', action='store_true',
        help='match mirrors that support IPv6')
    parser.add_argument(
        '-i', '--isos', action='store_true',
        help='match mirrors that host ISOs')
    parser.add_argument(
        '-l', '--limit', type=posint, metavar='n',
        help='limit output to this amount of results')
    parser.add_argument(
        '-o', '--output', type=Path, metavar='file',
        help='write the output to the specified file instead of stdout')
    args = parser.parse_args()

    if args.list_sortopts and args.list_countries:
        parser.error('Listing of options and countries is mutually exclusive.')

    return args


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

    basicConfig(level=INFO, format=LOG_FORMAT)
    args = get_args()
    mirrors = get_mirrors()

    if args.list_countries:
        return list_countries(mirrors, reverse=args.reverse)

    if args.list_sortopts:
        iterprint(sorted(mirrors.keys(), reverse=args.reverse))
        return 0

    mirrors = filter(partial(match, args), mirrors)

    if args.sort:
        key = partial(get_sorting_key, args.sort)
        mirrors = sorted(mirrors, key=key, reverse=args.reverse)

    if args.limit:
        mirrors = mirrors.head(args.limit)

    if not mirrors.size and args.limit != 0:
        LOGGER.error('No mirrors found.')
        return 1

    if args.limit is not None and len(mirrors) < args.limit:
        LOGGER.warning('Filter yielded less mirrors than specified limit.')

    if args.output:
        return dump_mirrors(mirrors, args.output)

    iterprint(get_mirrorlist(mirrors))
    return 0


if __name__ == '__main__':
    try:
        exit(main())
    except KeyboardInterrupt:
        LOGGER.error('Aborted by user.')
        exit(1)
