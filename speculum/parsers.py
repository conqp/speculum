"""Functions to parse data from command line arguments."""

from datetime import datetime, timedelta
from re import error, compile, Pattern  # pylint: disable=W0622


__all__ = ['hours', 'icstring', 'posint', 'regex', 'parse_datetime']


def hours(string: str) -> timedelta:
    """Returns a time delta for the given hours."""

    return timedelta(hours=int(string))


def icstring(string: str) -> string:
    """Returns a string with ignored case."""

    return string.casefold()


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
        raise ValueError(str(err))
