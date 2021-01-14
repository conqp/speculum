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

    config_parser = ConfigParser()

    if config_parser.read(filename):
        return config_parser

    raise ValueError(f'Invalid or malformed config file: {filename}')


def hours(string: str) -> timedelta:
    """Returns a time delta for the given hours."""

    return timedelta(hours=int(string))


def parse_datetime(string: str) -> datetime:
    """Parses a mirror's last_sync datetime stamp."""

    try:
        dtime = datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        dtime = datetime.strptime(string, '%Y-%m-%dT%H:%M:%SZ')

    return dtime.replace(tzinfo=None)


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
