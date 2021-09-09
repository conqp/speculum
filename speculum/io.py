"""Input / output and CLI utilities."""

from os import linesep
from pathlib import Path
from sys import stderr
from typing import Iterable

from speculum.logging import LOGGER


__all__ = ['dump_mirrors', 'iterprint']


def dump_mirrors(lines: Iterable[str], path: Path) -> bool:
    """Dumps the mirrors to the given path."""

    try:
        with path.open('w') as file:
            file.write(linesep.join(lines) + linesep)
    except PermissionError as permission_error:
        LOGGER.error(permission_error)
        return False

    return True


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
