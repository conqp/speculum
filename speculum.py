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
from pathlib import Path
from re import error, compile, Pattern  # pylint: disable=W0622
from sys import exit, stderr    # pylint: disable=W0622
from typing import Callable, Generator, Iterable, NamedTuple, Tuple
from urllib.request import urlopen
from urllib.parse import urlparse, ParseResult


MIRRORS_URL = 'https://www.archlinux.org/mirrors/status/json/'
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
REPO_PATH = '$repo/os/$arch'
LOG_FORMAT = '[%(levelname)s] %(name)s: %(message)s'
LOGGER = getLogger(__file__)


def strings(string: str) -> filter:
    """Splits strings by comma."""

    return filter(None, map(lambda s: s.strip().lower(), string.split(',')))


def stringtuple(string: str) -> Tuple[str]:
    """Returns a tuple of strings form a comma separated list."""

    return tuple(strings(string))


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


def get_json() -> dict:
    """Returns the mirrors from the respective URL."""

    with urlopen(MIRRORS_URL) as response:
        return load(response)


def get_mirrors() -> Generator[Mirror]:
    """Yields the respective mirrors."""

    for json in get_json()['urls']:
        yield Mirror.from_json(json)


def get_sorting_key(sorting: str) -> Callable:
    """Returns a key function to sort mirrors."""

    now = datetime.now()

    def key(mirror):
        return mirror.get_sorting_key(sorting, now)

    return key


def limit(mirrors: Iterable[Mirror], maximum: int) -> Generator[Mirror]:
    """Limit the amount of mirrors."""

    for count, mirror in enumerate(mirrors, start=1):
        if maximum is not None and count > maximum:
            break

        yield mirror


def get_args() -> Namespace:
    """Returns the parsed arguments."""

    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        '--sort', '-s', type=Sorting.from_string, default=None,
        metavar='sorting', help='sort by the respective property')
    parser.add_argument(
        '--reverse', '-r', action='store_true', help='sort in reversed order')
    parser.add_argument(
        '--countries', '-c', type=stringtuple, default=None,
        metavar='countries', help='match mirrors of these countries')
    parser.add_argument(
        '--protocols', '-p', type=stringtuple, default=None,
        metavar='protocols',
        help='match mirrors that use one of the specified protocols')
    parser.add_argument(
        '--max-age', '-a', type=hours, default=None, metavar='max_age',
        help='match mirrors that use one of the specified protocols')
    parser.add_argument(
        '--regex-incl', '-i', type=regex, default=None, metavar='regex_incl',
        help='match mirrors that match the regular expression')
    parser.add_argument(
        '--regex-excl', '-x', type=regex, default=None, metavar='regex_excl',
        help='exclude mirrors that match the regular expression')
    parser.add_argument(
        '--limit', '-l', type=int, default=None, metavar='file',
        help='limit output to this amount of results')
    parser.add_argument(
        '--output', '-o', type=Path, default=None, metavar='file',
        help='write the output to the specified file instead of stdout')
    return parser.parse_args()


def dump_mirrors(mirrors: Iterable[Mirror], path: Path) -> int:
    """Dumps the mirrors to the given path."""

    try:
        with path.open('w') as file:
            for mirror in mirrors:
                file.write(mirror.mirrorlist_record + '\n')
    except PermissionError as permission_error:
        LOGGER.error(permission_error)
        return 1

    return 0


def print_mirrors(mirrors: Iterable[Mirror]) -> int:
    """Prints the mirrors to STDOUT."""

    for mirror in mirrors:
        try:
            print(mirror.mirrorlist_record, flush=True)
        except BrokenPipeError:
            stderr.close()
            return 0

    return 0


def main() -> int:
    """Filters and sorts the mirrors."""

    basicConfig(level=INFO, format=LOG_FORMAT)
    args = get_args()
    mirrors = get_mirrors()
    filters = Filter(
        args.countries, args.protocols, args.max_age, args.regex_incl,
        args.regex_excl)
    mirrors = filter(filters.match, mirrors)
    key = get_sorting_key(args.sort)
    mirrors = sorted(mirrors, key=key, reverse=args.reverse)
    mirrors = limit(mirrors, args.limit)

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
    def from_string(cls, string: str) -> Tuple[Sorting]:
        """Returns a tuple of sortings from the respective string."""
        options = []

        for option in string.split(','):
            option = option.strip().lower()
            option = cls(option)
            options.append(option)

        return tuple(options)


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
        name = 'zzz' if self.name is None else self.name
        code = 'zz' if self.code is None else self.code
        return (name, code)


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

    def get_sorting_key(self, options: Tuple[Sorting], now: datetime) -> Tuple:
        """Returns a tuple of the soring keys in the desired order."""
        if not options:
            return ()

        key = []

        for option in options:
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

    countries: Tuple[str]
    protocols: Tuple[str]
    max_age: timedelta
    regex_incl: Pattern
    regex_excl: Pattern

    def match(self, mirror: Mirror) -> bool:
        """Matches the mirror."""
        if self.countries is not None:
            if not any(mirror.country.match(c) for c in self.countries):
                return False

        if self.protocols is not None:
            if mirror.url.scheme.lower() not in self.protocols:
                return False

        if self.max_age is not None:
            if mirror.last_sync + self.max_age < datetime.now():
                return False

        if self.regex_incl is not None:
            if not self.regex_incl.fullmatch(mirror.url.geturl()):
                return False

        if self.regex_excl is not None:
            if self.regex_excl.fullmatch(mirror.url.geturl()):
                return False

        return True


if __name__ == '__main__':
    exit(main())
