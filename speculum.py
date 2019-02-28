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

from __future__ import annotations
from argparse import ArgumentParser, Namespace
from datetime import datetime, timedelta
from enum import Enum
from json import load
from logging import INFO, basicConfig, getLogger
from os import linesep
from pathlib import Path
from re import error, compile, Pattern  # pylint: disable=W0622
from sys import exit, stderr    # pylint: disable=W0622
from typing import Callable, FrozenSet, Generator, Iterable, NamedTuple, Tuple
from urllib.request import urlopen
from urllib.parse import urlparse, ParseResult


MIRRORS_URL = 'https://www.archlinux.org/mirrors/status/json/'
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
REPO_PATH = '$repo/os/$arch'
LOG_FORMAT = '[%(levelname)s] %(name)s: %(message)s'
LOGGER = getLogger(__file__)


def strings(string: str) -> filter:
    """Yields non-empty stripped lower case strings, splitted by comma."""

    return filter(None, map(lambda s: s.strip().lower(), string.split(',')))


def hours(string: str) -> timedelta:
    """Returns a timedelta of the respective
    amount of hours from a string.
    """

    return timedelta(hours=int(string))


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


def get_mirrors() -> Generator[Mirror]:
    """Yields the respective mirrors."""

    for json in get_json()['urls']:
        yield Mirror.from_json(json)


def get_sorting_key(order: Tuple[Sorting]) -> Callable:
    """Returns a key function to sort mirrors."""

    now = datetime.now()

    def key(mirror):
        return mirror.get_sorting_key(order, now)

    return key


def limit(mirrors: Iterable[Mirror], maximum: int) -> Generator[Mirror]:
    """Limit the amount of mirrors."""

    for count, mirror in enumerate(mirrors, start=1):
        if maximum is not None and count > maximum:
            break

        yield mirror


def iterprint(items: Iterable[str]):
    """Prints the items one by one, catching BrokenPipeErrors."""

    for item in items:
        try:
            print(item, flush=True)
        except BrokenPipeError:
            stderr.close()
            break


def list_sorting_options(reverse: bool = False) -> int:
    """Lists available sorting options."""

    options = (option.value for option in Sorting)
    options = sorted(options, reverse=reverse)
    iterprint(options)
    return 0


def list_countries(mirrors: Iterable[Mirror], reverse: bool = False) -> int:
    """Lists available countries."""

    countries = map(lambda mirror: mirror.country, mirrors)
    countries = filter(lambda country: not country.empty, countries)
    countries = sorted(frozenset(countries), reverse=reverse)
    iterprint(f'{country.name} ({country.code})' for country in countries)
    return 0


def get_args() -> Namespace:
    """Returns the parsed arguments."""

    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        '--list-sortopts', '-S', action='store_true',
        help='list the available sorting options')
    parser.add_argument(
        '--list-countries', '-C', action='store_true',
        help='list the available countries')
    parser.add_argument(
        '--sort', '-s', nargs='+', type=Sorting, metavar='<option>',
        help='sort by the respective sort options')
    parser.add_argument(
        '--reverse', '-r', action='store_true', help='sort in reversed order')
    parser.add_argument(
        '--countries', '-c', nargs='+', metavar='<country>',
        help='match mirrors of these countries')
    parser.add_argument(
        '--protocols', '-p', nargs='+', metavar='<protocol>',
        help='match mirrors that use one of the specified protocols')
    parser.add_argument(
        '--max-age', '-a', type=hours, metavar='hours',
        help='match mirrors that use one of the specified protocols')
    parser.add_argument(
        '--regex-match', '-m', type=regex, metavar='regex',
        help='match mirrors that match the regular expression')
    parser.add_argument(
        '--regex-nomatch', '-n', type=regex, metavar='regex',
        help='exclude mirrors that match the regular expression')
    parser.add_argument(
        '--complete', '-t', action='store_true',
        help='match mirrors that are completely synced')
    parser.add_argument(
        '--active', '-u', action='store_true', help='match active mirrors')
    parser.add_argument(
        '--ipv4', '-4', action='store_true',
        help='match mirrors that support IPv4')
    parser.add_argument(
        '--ipv6', '-6', action='store_true',
        help='match mirrors that support IPv6')
    parser.add_argument(
        '--isos', '-i', action='store_true',
        help='match mirrors that host ISOs')
    parser.add_argument(
        '--limit', '-l', type=posint, metavar='n',
        help='limit output to this amount of results')
    parser.add_argument(
        '--output', '-o', type=Path, metavar='file',
        help='write the output to the specified file instead of stdout')
    args = parser.parse_args()

    if args.list_sortopts and args.list_countries:
        parser.error('Listing of options and countries is mutually exclusive.')

    return args


def dump_mirrors(mirrors: Iterable[Mirror], path: Path) -> int:
    """Dumps the mirrors to the given path."""

    mirrorlist = linesep.join(mirror.mirrorlist_record for mirror in mirrors)

    try:
        with path.open('w') as file:
            file.write(mirrorlist)
    except PermissionError as permission_error:
        LOGGER.error(permission_error)
        return 1

    return 0


def print_mirrors(mirrors: Iterable[Mirror]) -> int:
    """Prints the mirrors to STDOUT."""

    iterprint(mirror.mirrorlist_record for mirror in mirrors)
    return 0


def main() -> int:
    """Filters and sorts the mirrors."""

    basicConfig(level=INFO, format=LOG_FORMAT)
    args = get_args()

    if args.list_sortopts:
        return list_sorting_options(reverse=args.reverse)

    mirrors = get_mirrors()

    if args.list_countries:
        return list_countries(mirrors, reverse=args.reverse)

    fltr = Filter.from_args(args)
    mirrors = filter(fltr.match, mirrors)
    sorting_key = get_sorting_key(args.sort)
    mirrors = sorted(mirrors, key=sorting_key, reverse=args.reverse)
    mirrors = limit(mirrors, args.limit)
    mirrors = tuple(mirrors)

    if not mirrors and args.limit != 0:
        LOGGER.error('No mirrors found.')
        return 1

    if args.limit is not None and len(mirrors) < args.limit:
        LOGGER.warning('Filter yielded less mirrors than specified limit.')

    if args.output:
        return dump_mirrors(mirrors, args.output)

    return print_mirrors(mirrors)


class Sorting(Enum):
    """Sorting options."""

    AGE = 'age'
    RATE = 'rate'
    COUNTRY = 'country'
    SCORE = 'score'
    DELAY = 'delay'

    @classmethod
    def from_string(cls, string: str) -> Generator[Sorting]:
        """Returns a tuple of sortings from the respective string."""
        for option in strings(string):
            yield cls(option)


class Duration(NamedTuple):
    """Represents the duration data on a mirror."""

    average: float
    stddev: float

    @property
    def sorting_key(self) -> Tuple[float]:
        """Returns a sorting key."""
        average = float('inf') if self.average is None else self.average
        stddev = float('inf') if self.stddev is None else self.stddev
        return (average, stddev)


class Country(NamedTuple):
    """Represents country information."""

    name: str
    code: str

    def match(self, string: str) -> bool:
        """Matches a country description."""
        return string.lower() in {self.name.lower(), self.code.lower()}

    @property
    def sorting_key(self) -> Tuple[str]:
        """Returns a sorting key."""
        return (self.name or '~', self.name or '~')

    @property
    def empty(self):
        """Determines whether there is not country information available."""
        return not self.name and not self.code


class Mirror(NamedTuple):
    """Represents information about a mirror."""

    url: ParseResult
    last_sync: datetime
    completion: float
    delay: int
    duration: Duration
    score: float
    active: bool
    country: Country
    isos: bool
    ipv4: bool
    ipv6: bool
    details: ParseResult

    @classmethod
    def from_json(cls, json: dict) -> Mirror:
        """Returns a new mirror from a JSON-ish dict."""
        url = urlparse(json['url'])
        last_sync = json['last_sync']

        if last_sync is not None:
            last_sync = datetime.strptime(last_sync, DATE_FORMAT).replace(
                tzinfo=None)

        duration_avg = json['duration_avg']
        duration_stddev = json['duration_stddev']
        duration = Duration(duration_avg, duration_stddev)
        country = json['country']
        country_code = json['country_code']
        country = Country(country, country_code)
        details = urlparse(json['details'])
        return cls(
            url, last_sync, json['completion_pct'], json['delay'], duration,
            json['score'], json['active'], country, json['isos'], json['ipv4'],
            json['ipv6'], details)

    @property
    def mirrorlist_url(self) -> ParseResult:
        """Returns a mirror list URL."""
        scheme, netloc, path, params, query, fragment = self.url

        if not path.endswith('/'):
            path += '/'

        return ParseResult(
            scheme, netloc, path + REPO_PATH, params, query, fragment)

    @property
    def mirrorlist_record(self) -> str:
        """Returns a mirror list record."""
        return f'Server = {self.mirrorlist_url.geturl()}'

    def get_sorting_key(self, order: Tuple[Sorting], now: datetime) -> Tuple:
        """Returns a tuple of the soring keys in the desired order."""
        if not order:
            return ()

        key = []

        for option in order:
            if option == Sorting.AGE:
                if self.last_sync is None:
                    key.append(now - datetime.fromtimestamp(0))
                else:
                    key.append(now - self.last_sync)
            elif option == Sorting.RATE:
                key.append(self.duration.sorting_key)
            elif option == Sorting.COUNTRY:
                key.append(self.country.sorting_key)
            elif option == Sorting.SCORE:
                key.append(float('inf') if self.score is None else self.score)
            elif option == Sorting.DELAY:
                key.append(float('inf') if self.delay is None else self.delay)
            else:
                raise ValueError(f'Invalid sorting option: {option}.')

        return tuple(key)


class Filter(NamedTuple):
    """Represents a set of mirror filtering options."""

    countries: FrozenSet[str]
    protocols: FrozenSet[str]
    max_age: timedelta
    regex_match: Pattern
    regex_nomatch: Pattern
    complete: bool
    active: bool
    ipv4: bool
    ipv6: bool
    isos: bool

    @classmethod
    def from_args(cls, args):
        """Returns a filter instance from the respective CLI arguments."""
        return cls(
            args.countries, args.protocols, args.max_age, args.regex_match,
            args.regex_nomatch, args.complete, args.active, args.ipv4,
            args.ipv6, args.isos)

    def match_fails(self, mirror: Mirror) -> bool:
        """Yields True on failed matches."""
        # Boolean tests first.
        yield self.active and not mirror.active
        yield self.ipv4 and not mirror.ipv4
        yield self.ipv6 and not mirror.ipv6
        yield self.isos and not mirror.isos

        # Other, slower checks.
        if self.complete is not None:
            yield mirror.completion < 1

        if self.countries is not None:
            yield not any(mirror.country.match(c) for c in self.countries)

        if self.protocols is not None:
            yield mirror.url.scheme.lower() not in self.protocols

        if self.max_age is not None:
            yield mirror.last_sync + self.max_age < datetime.now()

        if self.regex_match is not None:
            yield self.regex_match.match(mirror.url.geturl())

        if self.regex_nomatch is not None:
            yield self.regex_nomatch.match(mirror.url.geturl())

    def match(self, mirror: Mirror) -> bool:
        """Matches the mirror."""
        return not any(self.match_fails(mirror))


if __name__ == '__main__':
    try:
        exit(main())
    except KeyboardInterrupt:
        LOGGER.error('Aborted by user.')
        exit(1)
