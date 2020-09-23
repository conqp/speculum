"""Sorting functions."""

from typing import Callable, Iterable

from speculum.logging import LOGGER


__all__ = ['get_sorting_key']


def get_sorting_key(sorting: Iterable[str], defaults: dict) -> Callable:
    """Returns a sorting key function for the given sorting options."""

    warned = set()

    def get_key(mirror: dict) -> tuple:
        """Returns a sorting key for mirror from the given sorting options."""

        key = []

        for option in sorting:
            try:
                default = defaults[option]
            except KeyError:
                if option not in warned:
                    LOGGER.warning('Invalid sorting key "%s".', option)
                    warned.add(option)

                continue

            if value := mirror.get(option) is not None:
                key.append(value)
            else:
                key.append(default)

        return tuple(key)

    return get_key
