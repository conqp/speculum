"""Configuration file parsing."""

from __future__ import annotations
from argparse import Namespace
from configparser import ConfigParser
from pathlib import Path
from re import error, compile, Pattern  # pylint: disable=W0622
from typing import List, NamedTuple

from speculum.logging import LOGGER


__all__ = ['Configuration']


def get_strings(parser: ConfigParser, section: str, key: str) -> List[str]:
    """Returns a list of strings from the
    key in the section iff it is not empty.
    """

    if string := parser.get(section, key, fallback=None):
        return string.split()

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
    output: Path

    def __or__(self, other):
        if other is None:
            return self

        args = (o if s is None else s for s, o in zip(self, other))
        return type(self)(*args)

    def __ror__(self, other):
        if other is None:
            return self

        return other | self

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
            args.output
        )

    @classmethod
    def from_parser(cls, parser: ConfigParser) -> Configuration:
        """Creates the configuration from the given args."""
        return cls(
            get_strings(parser, 'sorting', 'sort'),
            parser.getboolean('sorting', 'reverse', fallback=False),
            get_strings(parser, 'filtering', 'countries'),
            get_strings(parser, 'filtering', 'protocols'),
            parser.getint('filtering', 'max_age', fallback=None),
            get_regex(parser, 'filtering', 'match'),
            get_regex(parser, 'filtering', 'nomatch'),
            parser.getboolean('filtering', 'complete', fallback=False),
            parser.getboolean('filtering', 'active', fallback=False),
            parser.getboolean('filtering', 'ipv4', fallback=False),
            parser.getboolean('filtering', 'ipv6', fallback=False),
            parser.getboolean('filtering', 'isos', fallback=False),
            parser.getint('output', 'limit', fallback=None),
            get_path(parser, 'output', 'file')
        )

    @classmethod
    def load(cls, args: Namespace) -> Configuration:
        """Loads the configuration from the arguments."""
        config = cls.from_parser(args.config) if args.config else None
        return config | cls.from_args(args)
