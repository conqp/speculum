"""Configuration file parsing."""

from __future__ import annotations
from argparse import Namespace
from configparser import ConfigParser
from pathlib import Path
from re import error, compile, Pattern  # pylint: disable=W0622
from typing import Iterable, List, NamedTuple

from speculum.logging import LOGGER


__all__ = ['Configuration']


def get_cistrings(parser: ConfigParser, section: str, key: str) -> List[str]:
    """Returns a list of casefold strings from
    the key in the section iff it is not empty.
    """

    if string := parser.get(section, key, fallback=None):
        if ',' in string:
            return [string.strip().casefold() for string in string.split(',')]

        return [string.casefold() for string in string.split()]

    return None


def get_regex(parser: ConfigParser, section: str, key: str) -> Pattern:
    """Returns a regular expression if available."""

    if regex := parser.get(section, key, fallback=None):
        try:
            return compile(regex)
        except error:
            LOGGER.error('Invalid regular expression: %s', regex)

    return None


def get_path(parser: ConfigParser, section: str, key: str) -> Path:
    """Returns a path if available."""

    if path := parser.get(section, key, fallback=None):
        try:
            return Path(path)
        except ValueError:
            LOGGER.error('Invalid path: %s', path)

    return None


class Configuration(NamedTuple):
    """Configuration settings for speculum."""

    sort: List[str]
    reverse: bool
    countries: List[str]
    protocols: List[str]
    max_age: int
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
            args.reverse or None,
            args.countries,
            args.protocols,
            args.max_age,
            args.match,
            args.nomatch,
            args.complete or None,
            args.active or None,
            args.ipv4 or None,
            args.ipv6 or None,
            args.isos or None,
            args.limit,
            args.header or None,
            args.output
        )

    @classmethod
    def from_parser(cls, parser: ConfigParser) -> Configuration:
        """Creates the configuration from the given args."""
        return cls(
            get_cistrings(parser, 'sorting', 'sort'),
            parser.getboolean('sorting', 'reverse', fallback=None),
            get_cistrings(parser, 'filtering', 'countries'),
            get_cistrings(parser, 'filtering', 'protocols'),
            parser.getint('filtering', 'max_age', fallback=None),
            get_regex(parser, 'filtering', 'match'),
            get_regex(parser, 'filtering', 'nomatch'),
            parser.getboolean('filtering', 'complete', fallback=None),
            parser.getboolean('filtering', 'active', fallback=None),
            parser.getboolean('filtering', 'ipv4', fallback=None),
            parser.getboolean('filtering', 'ipv6', fallback=None),
            parser.getboolean('filtering', 'isos', fallback=None),
            parser.getint('output', 'limit', fallback=None),
            parser.getboolean('output', 'header', fallback=None),
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
        args = (s if o is None else o for s, o in zip(self, other))
        return type(self)(*args)

    def lines(self, none: bool = False) -> Iterable[str]:
        """Yield lines of keys and values."""
        for key, value in self._asdict().items():   # pylint: disable=E1101
            if none or value is not None:
                yield f'{key} = {value}'
