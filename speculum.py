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
from datetime import datetime
from json import load
from logging import INFO, basicConfig, getLogger
from os import linesep
from pathlib import Path
from re import error, compile, Pattern  # pylint: disable=W0622
from sys import exit, stderr    # pylint: disable=W0622
from typing import Iterable
from urllib.request import urlopen
from urllib.parse import urlparse, ParseResult

from pandas import to_datetime, DataFrame


MIRRORS_URL = 'https://www.archlinux.org/mirrors/status/json/'
REPO_PATH = '$repo/os/$arch'
LOG_FORMAT = '[%(levelname)s] %(name)s: %(message)s'
LOGGER = getLogger(__file__)


def regex(string: str) -> Pattern:
    """Returns a regular expression."""

    try:
        return compile(string)
    except error:
        raise ValueError(str(error))


def posint(string: str) -> int:
    """Returns a positive integer."""

    integer = int(string)

    if integer > 0:
        return integer

    raise ValueError('Integer must be greater than zero.')


def get_json() -> dict:
    """Returns the mirrors from the respective URL."""

    with urlopen(MIRRORS_URL) as response:
        return load(response)


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


def get_mirrorlist(mirrors: DataFrame) -> Iterable[str]:
    """Returns a mirror list record."""

    for record in mirrors.itertuples():
        url = mirror_url(record.url)
        yield f'Server = {url}'


def list_countries(mirrors: DataFrame, reverse: bool = False) -> int:
    """Lists available countries."""

    records = mirrors.itertuples()
    countries = map(lambda rec: (rec.country, rec.country_code), records)
    countries = filter(lambda country: country[0] and country[1], countries)
    countries = sorted(frozenset(countries), reverse=reverse)
    iterprint(f'{name} ({code})' for name, code in countries)
    return 0


def filter_mirrors(mirrors: DataFrame, args: Namespace) -> DataFrame:
    """Filters the respective mirrors."""

    if args.countries is not None:
        mirrors = mirrors[
            mirrors.country.str.lower().isin(args.countries)
            | mirrors.country_code.str.lower().isin(args.countries)]

    if args.protocols is not None:
        mirrors = mirrors[mirrors.protocol.isin(args.protocols)]

    if args.max_age is not None:
        mirrors = mirrors[mirrors.age <= args.max_age]

    if args.regex_match is not None:
        mirrors = mirrors[mirrors.url.str.match(args.regex_match)]

    if args.regex_nomatch is not None:
        mirrors = mirrors[~mirrors.url.str.match(args.regex_nomatch)]

    if args.complete:
        mirrors = mirrors[mirrors.completion_pct == 1]

    if args.active:
        mirrors = mirrors[mirrors.active]

    if args.ipv4:
        mirrors = mirrors[mirrors.ipv4]

    if args.ipv6:
        mirrors = mirrors[mirrors.ipv6]

    if args.isos:
        mirrors = mirrors[mirrors.isos]

    return mirrors


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
        '-a', '--max-age', type=posint, metavar='hours',
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


def dump_mirrors(mirrors: DataFrame, path: Path) -> int:
    """Dumps the mirrors to the given path."""

    mirrorlist = linesep.join(get_mirrorlist(mirrors))

    try:
        with path.open('w') as file:
            file.write(mirrorlist + linesep)
    except PermissionError as permission_error:
        LOGGER.error(permission_error)
        return 1

    return 0


def print_mirrors(mirrors: DataFrame) -> int:
    """Prints the mirrors to STDOUT."""

    iterprint(get_mirrorlist(mirrors))
    return 0


def main() -> int:
    """Filters and sorts the mirrors."""

    basicConfig(level=INFO, format=LOG_FORMAT)
    args = get_args()
    mirrors = DataFrame(get_json()['urls'])

    if args.list_countries:
        return list_countries(mirrors, reverse=args.reverse)

    last_sync = to_datetime(mirrors.last_sync).dt.tz_convert(None)
    timediff = datetime.now() - last_sync
    mirrors['age'] = timediff.dt.total_seconds() / 3600
    columns = mirrors.columns.values

    if args.list_sortopts:
        iterprint(sorted(columns, reverse=args.reverse))
        return 0

    mirrors = filter_mirrors(mirrors, args)

    if args.sort:
        try:
            mirrors = mirrors.sort_values(
                args.sort, ascending=not args.reverse)
        except KeyError as key:
            LOGGER.error('Cannot sort by key %s.', key)
            return 1

    if args.limit:
        mirrors = mirrors.head(args.limit)

    if not mirrors.size and args.limit != 0:
        LOGGER.error('No mirrors found.')
        return 1

    if args.limit is not None and len(mirrors) < args.limit:
        LOGGER.warning('Filter yielded less mirrors than specified limit.')

    if args.output:
        return dump_mirrors(mirrors, args.output)

    return print_mirrors(mirrors)


if __name__ == '__main__':
    try:
        exit(main())
    except KeyboardInterrupt:
        LOGGER.error('Aborted by user.')
        exit(1)
