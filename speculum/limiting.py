"""Limiting of mirrors."""

from typing import Iterable, Iterator, Optional


__all__ = ['limit']


def limit(mirrors: Iterable[dict], maximum: Optional[int]) -> Iterator[dict]:
    """Yields mirrors up to the specified maximum."""

    for count, mirror in enumerate(mirrors, start=1):
        if maximum is not None and count > maximum:
            break

        yield mirror
