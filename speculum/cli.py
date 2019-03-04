"""Command line tools."""

from sys import stderr
from typing import Iterable


__all__ = ['iterprint']


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
