"""Configuration file parsing."""

from __future__ import annotations
from argparse import Namespace
from configparser import ConfigParser
from datetime import timedelta
from pathlib import Path
from re import error, compile, Pattern  # pylint: disable=W0622
from typing import Iterator, NamedTuple, Optional

from speculum.logging import LOGGER


__all__ = ['Configuration']


def get_cistrings(parser: ConfigParser, section: str,
                  key: str) -> list[str]:
    """Returns a list of casefold strings from
    the key in the section iff it is not empty.
    """

    if string := parser.get(section, key, fallback=None):
        if ',' in string:
            return [string.strip().casefold() for string in string.split(',')]

        return [string.casefold() for string in string.split()]

    return []


def get_hours(parser: ConfigParser, section: str,
              key: str) -> Optional[timedelta]:
    """Returns a timedelta of hours if available."""

    if (hours := parser.getint(section, key, fallback=None)) is not None:
        return timedelta(hours=hours)

    return None


def get_path(parser: ConfigParser, section: str, key: str) -> Optional[Path]:
    """Returns a path if available."""

    if path := parser.get(section, key, fallback=None):
        try:
            return Path(path)
        except ValueError:
            LOGGER.error('Invalid path: %s', path)

    return None


def get_regex(parser: ConfigParser, section: str,
              key: str) -> Optional[Pattern]:
    """Returns a regular expression if available."""

    if regex := parser.get(section, key, fallback=None):
        try:
            return compile(regex)
        except error:
            LOGGER.error('Invalid regular expression: %s', regex)

    return None


class Configuration(NamedTuple):
    """Configuration settings for speculum."""

    sort: list[str]
    reverse: bool
    countries: list[str]
    protocols: list[str]
    max_age: timedelta
    match: Pattern
    nomatch: Pattern
    complete: bool
    active: bool
    ipv4: bool
    ipv6: bool
    isos: bool
    limit: int
    header: bool
    output: Path

    @classmethod
    def from_args(cls, args: Namespace) -> Configuration:
        """Creates the configuration from the given args."""
        return cls(
            args.sort,
            args.reverse,
            args.countries,
            args.protocols,
            args.max_age,
            args.match,
            args.nomatch,
            args.complete,
            args.active,
            args.ipv4,
            args.ipv6,
            args.isos,
            args.limit,
            args.header,
            args.output
        )

    @classmethod
    def from_parser(cls, parser: ConfigParser) -> Configuration:
        """Creates the configuration from the given args."""
        return cls(
            get_cistrings(parser, 'sorting', 'sort'),
            parser.getboolean('sorting', 'reverse', fallback=False),
            get_cistrings(parser, 'filtering', 'countries'),
            get_cistrings(parser, 'filtering', 'protocols'),
            get_hours(parser, 'filtering', 'max_age'),
            get_regex(parser, 'filtering', 'match'),
            get_regex(parser, 'filtering', 'nomatch'),
            parser.getboolean('filtering', 'complete', fallback=False),
            parser.getboolean('filtering', 'active', fallback=False),
            parser.getboolean('filtering', 'ipv4', fallback=False),
            parser.getboolean('filtering', 'ipv6', fallback=False),
            parser.getboolean('filtering', 'isos', fallback=False),
            parser.getint('output', 'limit', fallback=None),
            parser.getboolean('output', 'header', fallback=False),
            get_path(parser, 'output', 'file')
        )

    @classmethod
    def load(cls, args: Namespace) -> Configuration:
        """Loads the configuration from the arguments."""
        config = cls.from_args(args)

        if args.config:
            return cls.from_parser(args.config).update(config)

        return config

    def update(self, other: Configuration) -> Configuration:
        """Returns a new configuration with properties overridden
        by another configuration iff they are not None.
        """
        return type(self)(*(o or s for s, o in zip(self, other)))

    def lines(self, none: bool = False) -> Iterator[str]:
        """Yield lines of keys and values."""
        for key, value in self._asdict().items():   # pylint: disable=E1101
            if none or value is not None:
                yield f'{key} = {value}'
