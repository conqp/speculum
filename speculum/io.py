"""Input / output and CLI utilities."""

from functools import wraps
from os import linesep
from pathlib import Path
from sys import exit, stderr    # pylint: disable=W0622
from typing import Iterable

from speculum.logging import LOGGER


__all__ = ['dump_mirrors', 'iterprint']


def dump_mirrors(lines: Iterable[str], path: Path) -> bool:
    """Dumps the mirrors to the given path."""

    mirrorlist = linesep.join(lines)

    try:
        with path.open('w') as file:
            file.write(mirrorlist + linesep)
    except PermissionError as permission_error:
        LOGGER.error(permission_error)
        return False

    return True


def exiting(function):
    """Makes a function exit with the returned exit code."""

    @wraps(function)
    def wrapper(*args, **kwargs):
        exit(function(*args, **kwargs))

    return wrapper


def iterprint(items: Iterable[str]):
    """Prints the items one by one, catching BrokenPipeErrors so
    that output can be handled by head, tail or similar programs.
    """

    for item in items:
        try:
            print(item, flush=True)
        except BrokenPipeError:
            stderr.close()
            break
