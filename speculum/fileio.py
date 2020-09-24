"""File input and output."""

from os import linesep
from pathlib import Path
from typing import Iterable

from speculum.logging import LOGGER


__all__ = ['dump_mirrors']


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
