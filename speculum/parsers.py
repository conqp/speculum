"""Functions to parse data from command line arguments."""

from configparser import ConfigParser
from datetime import datetime, timedelta
from re import error, compile, Pattern  # pylint: disable=W0622


__all__ = [
    'configfile',
    'hours',
    'posint',
    'regex',
    'parse_datetime'
]


def configfile(filename: str) -> ConfigParser:
    """Reads a configuration file."""

    if (config_parser := ConfigParser()).read(filename):
        return config_parser

    raise ValueError(f'Invalid or malformed config file: {filename}')


def hours(string: str) -> timedelta:
    """Returns a time delta for the given hours."""

    return timedelta(hours=int(string))


def parse_datetime(string: str) -> datetime:
    """Parses a mirror's last_sync datetime stamp."""

    if string.endswith('Z'):
        string = string[:-1]

    return datetime.fromisoformat(string).replace(tzinfo=None)


def posint(string: str) -> int:
    """Returns a positive integer."""

    if (integer := int(string)) > 0:
        return integer

    raise ValueError('Integer must be greater than zero.')


def regex(string: str) -> Pattern:
    """Returns a regular expression."""

    try:
        return compile(string)
    except error as err:
        raise ValueError(str(err)) from None
