"""Sorting functions."""

from typing import Any, Callable, Iterable

from speculum.logging import LOGGER


__all__ = ["get_sorting_key"]


def get_sorting_key(
    sorting: Iterable[str], defaults: dict
) -> Callable[[dict], tuple[Any, ...]]:
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

            key.append(mirror.get(option, default))

        return tuple(key)

    return get_key
