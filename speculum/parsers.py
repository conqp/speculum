"""Functions to parse data from command line arguments."""

from configparser import ConfigParser
from datetime import datetime, timedelta
from re import error, compile, Pattern  # pylint: disable=W0622


__all__ = [
    'cistring',
    'configfile',
    'hours',
    'posint',
    'regex',
    'parse_datetime'
]


def cistring(string: str) -> str:
    """Returns a string with ignored case."""

    return string.casefold()


def configfile(string: str) -> ConfigParser:
    """Reads a configuration file."""

    config_parser = ConfigParser()

    if config_parser.read(string):
        return config_parser

    raise ValueError('Invalid or malformed config file: {string}')


def hours(string: str) -> timedelta:
    """Returns a time delta for the given hours."""

    return timedelta(hours=int(string))


def parse_datetime(string: str) -> datetime:
    """Parses a mirror's last_sync datetime stamp."""

    return datetime.fromisoformat(string).replace(tzinfo=None)


def posint(string: str) -> int:
    """Returns a positive integer."""

    integer = int(string)

    if integer > 0:
        return integer

    raise ValueError('Integer must be greater than zero.')


def regex(string: str) -> Pattern:
    """Returns a regular expression."""

    try:
        return compile(string)
    except error as err:
        raise ValueError(str(err)) from None
